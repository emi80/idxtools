"""Index module.

The module provide classes to perform operations on index files.

"""
import re
import os
import sys
from copy import deepcopy
from indexfile.utils import *




# setup logger
import indexfile
# Disable warning about invalid constant name
# pylint: disable=C0103
log = indexfile.getLogger(__name__)
# pylint: enable=C0103


class Dataset(object):
    """A class that represent dataset in the index file.

    Each entry is identified by a dataset id (eg. labExpId) and has metadata
    information as long as file information.
    """

    def __init__(self, fileinfo=None, **kwargs):
        """Create an instance of a Dataset. ``kwargs`` contains
        the dataset attributes.

        """
        self.__dict__['_metadata'] = {}
        self.__dict__['_files'] = DotDict()
        self.__dict__['_attributes'] = {}

        if not fileinfo:
            fileinfo = indexfile.default_format.get('fileinfo')

        is_file = False

        for key, val in kwargs.items():
            if key in fileinfo:
                is_file = True
                continue
            if not val or val == '':
                val = 'NA'
            self.__setattr__(key, val)

        if is_file:
            self.add_file(**kwargs)

    def add_file(self, update=False, fileinfo=None, **kwargs):
        """Add a file to the dataset files dictionary. ``kwargs`` contains
        the file information. 'path' and 'type' argument are mandatory in order
        to add the file.

        """

        path = kwargs.get('path')
        file_type = kwargs.get('type')

        if not fileinfo:
            fileinfo = indexfile.default_format.get('fileinfo')

        if not path:
            log.debug('No path specified. Add metadata entry')
            path = '.'

        if not file_type:
            log.debug('Get file type from file extension')
            file_type = os.path.splitext(path)[1].strip('.')
            kwargs['type'] = file_type

        existing_type = self.find_file(path)

        if existing_type:
            if not update:
                log.debug("Skip existing %s entry", path)
                return
            log.debug("Update %s entry", path)
            if file_type != existing_type:
                self.rm_file(path=path)

        if not self._files.get(file_type):
            log.debug('Create file type dictionary for %s', file_type)
            self._files[file_type] = DotDict()

        if (not path in self._files.get(file_type).keys()) or update:
            log.debug('Create entry for %s', path)
            self._files.get(file_type)[path] = DotDict()

        info = self._files.get(file_type).get(path)

        for key, val in kwargs.items():
            if key == 'path' or key not in fileinfo:
                continue
            if not val or val == '':
                log.debug('Replace missing value with NA for %s', key)
                val = 'NA'
            info[key] = val


    def find_file(self, path):
        """Look for sepcified file inot the dataset"""
        for ftype, files in self._files.items():
            if path in files.keys():
                return ftype
        return None


    def rm_file(self, **kwargs):
        """Remove a file form the dataset files dictionary. ``kwargs`` contains
        the file information. The 'path' argument is mandatory in order
        to delete the file.

        """

        path = kwargs.get('path')
        type = kwargs.get('type')

        if not path and not type:
            log.debug('No file path and type specified')
            return

        if not type:
            for key, val in self._files.items():
                if path in val:
                    type = key
                    log.debug('Found file type entry for %s', path)
                    break
            else:
                log.debug('No file type entry found for %s', path)
                return
            log.debug('Delete entry for %s', path)
            del self._files.get(type)[path]
            if not self._files.get(type):
                log.debug('Delete file type entry for %s', type)
                del self._files[type]
        else:
            log.debug('Delete all %r entries', type)
            del self._files[type]

    def export(self, types=None, tags=None):
        """Export a :class:Dataset object to a list of dictionaries (one for
        each file).

        :keyword types: the list of file types to be exported. If set only the
        file types in the list are exported. Default: None (all types
        exported).

        :keyword tags: the list of tags to be exported. If set only the
        sepcified tags will be put on output. Default: Nene (all tags exported)
        """
        out = []
        if not tags:
            tags = self._metadata.keys() + ['path', 'type']
            if self._files:
                tags += [k for infos in self._files.values()
                         for info in infos.values()
                         for k in info.keys()]
            tags = list(set(tags))
        if not types:
            types = self._files.keys()
        if type(types) == str:
            types = [types]
        if type(tags) == str:
            tags = [tags]
        # if 'id' not in tags:
        #     tags.append('id')
        if not self._files:
            log.debug('No files found in the index. Write metadata index')
            return [dict([(k, v) for k, v in self._metadata.items()
                    if k in tags])]
        for ftype in types:
            log.debug('Export type %r', ftype)
            for path, info in getattr(self, ftype).items():
                data = dict([(k, v) for k, v in self._metadata.items()
                            + {'path': path, 'type': ftype}.items()
                            + info.items() if k in tags])
                out.append(data)
        return out

    def get_meta_tags(self):
        """Return all metadata tag names"""
        return self._metadata.keys()

    def get_meta_items(self):
        """Return all metadata tag key value pairs"""
        return self._metadata.items()

    def get_tags(self, tags=None, exclude=None):
        """Concatenate specified tags. The tag are formatted according to the
        index file format

        :keyword tags: list of keys to be included into output. Default: None
        (all tags returned).
        :keyword exclude: list of keys to be excluded from output. Default:
        None (all keys included).

        """
        if not tags:
            tags = self._metadata.keys()
        if exclude is None:
            exclude = []
        if type(tags) == str:
            tags = [tags]
        if type(exclude) == str:
            exclude = [exclude]

        tags = list(set(tags).difference(set(exclude)))
        data = dict([i for i in self._metadata.iteritems() if i[0] in tags])
        return to_tags(**data)

    def merge(self, datasets, sep=','):
        """Merge metadata of this dataset with the ones from another dataset

        :param datasets: A list of datasets to be merged with the current
        dataset
        """
        if type(datasets) != list and hasattr(datasets, 'id'):
            datasets = [datasets]
        dsid = sep.join([self.id] + [d.id for d in datasets])
        meta = {}
        for k in set(self._metadata.keys() + [
                j for d1 in datasets for j in d1.get_meta_tags()]):
            vals = [self._metadata.get(k)] + [
                getattr(d, k) for d in datasets]
            meta[k] = vals if len(set(vals)) > 1 else vals[0]
        meta['id'] = dsid
        d = Dataset(**meta)
        return d

    def __getattr__(self, name):
        if name in self.__dict__['_attributes'].keys():
            return self.__dict__['_attributes'][name](self)
        if name in self._metadata.keys():
            return self._metadata.get(name)
        if name in self._files.keys():
            return self._files.get(name)
        raise AttributeError('%r object has no attribute %r' % (
            self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name != '__dict__':
            self.__dict__['_metadata'][name] = value

    def __repr__(self):
        return "(Dataset %s)" % (self.id)

    def __str__(self):
        return self.get_tags()

    def __iter__(self):
        """
        Iterates over all files in a dataset. Returns a tuple containing the
        path and a dictionary with the file information.
        """
        for files in self._files.values():
            for path, info in files.items():
                yield (path, info)

    def __len__(self):
        return len([f for l in self._files.values() for f in l])


class Index(object):
    """A class to access information stored into 'index files'.
    """

    def __init__(self, path=None, datasets=None, format=None):
        """Creates an instance of an Index

        :param path: the path to the index file
        :keyword datasets: a list containing all the entries as dictionaries.
        Default: None.
        :keyword format: a dictionary containing the format and mapping
        information. Default: None.

        The format information can be expressed with a dictionary as follows:

        :key fileinfo: a list with the names of the keys related to files
        :key id: the dataset identifier name. Default: 'id'
        :key map: a dictionary contatining the mapping information
        :key sep: the key/value separator character
        :key trail: the key/value pair trailing character
        :key kw_sep: the keywords separator character

        """

        if path:
            path = os.path.abspath(path)
        self.path = path

        self.datasets = datasets or {}
        self._lock = None
        self.format = format or deepcopy(indexfile.default_format)
        self._lookup = {}
        self._alltags = []

    def open(self, path=None):
        """Open a file and load/import data into the index

        :param path: the path to the input file

        """
        if not path:
            if not self.path:
                raise AttributeError('No path sepcified')
            log.debug('Use path from Index instance: %s', self.path)
            path = self.path
        log.debug('Open %s', path)
        if type(path) == str:
            with open(os.path.abspath(path), 'r') as index_file:
                self._open_file(index_file)
            self.path = os.path.abspath(path)
        if type(path) == file:
            self._open_file(path)
            if path is not sys.stdin:
                self.path = os.path.abspath(path.name)

    def set_format(self, input_format):
        """Set index format from json string or file

        :param str: the input string. It can be a path to a file or a valid
        json string.

        """

        import simplejson as json

        if not input_format:
            log.debug('Use default indexfile format')
            input_format = indexfile.default_format

        log.debug('Load format %s', input_format)
        try:
            format_file = open(input_format, 'r')
            self.format = json.load(format_file)
        # Disable pylint message about no exception type specifies
        # pylint: disable=W0702
        except:
            self.format = json.loads(input_format)
        # pylint: enable=W0702

    def _open_file(self, index_file):
        """Open index file"""

        if self.datasets:
            log.debug("Overwritie exisitng data")
            del self.datasets
            self.datasets = {}
        if index_file == sys.stdin:
            import tempfile
            log.debug('Create temporary file for %s', index_file)
            index_file = tempfile.TemporaryFile()
            for line in sys.stdin:
                index_file.write("%s" % line)
            index_file.seek(0)
        log.debug('Guess file format')
        dummy_file_type, dialect = Index.guess_type(index_file)
        index_file.seek(0)
        if dialect:
            log.debug('Load table file with %s', dialect)
            self._load_table(index_file, dialect)
        else:
            log.debug('Load indexfile')
            self._load_index(index_file)

    def _load_index(self, index_file):
        """Load a file complying with the index file format.

        :param index_file: a :class:`file` object pointing to the input file

        """
        for line in index_file:
            tags = Index.parse_line(line, **self.format)

            dataset = self.insert(**tags)

    def _load_table(self, index_file, dialect=None):
        """Import entries from a SV file. The sv file must have an header line
        with the name of the attributes.

        :param index_file: a :class:`file` object pointing to the input file
        :keyword dialect: a :class:`csv.dialect` containg the input file
        format information

        """
        import csv

        reader = csv.DictReader(index_file, dialect=dialect)
        for line in reader:
            tags = Index.map_keys(line, **self.format)
            dataset = self.insert(**tags)

    def find_replicates(self, **kwargs):
        """Try to find replicates in the index using a dataset id made from
        the concatenation of multiple dataset ids
        """
        if not kwargs.get('id'):
            return None
        ids = kwargs.get('id').split(',')
        datasets = dict([
            (k, self.datasets[k]) for k in ids if k in self.datasets])
        if not datasets:
            return []
        if len(datasets) != len(ids):
            raise ValueError('Some of the ids for the replicate do not exist. \
                Please check the dataset ids')
        return [datasets[k] for k in sorted(datasets.keys())]

    def insert(self, update=False, dataset=None, **kwargs):
        """Add a dataset to the index. Keyword arguments contains the dataset
        attributes.

        :keyword update: specifies whether existing values has to be updated
        :keyword dataset: the :class:`Dataset` to be inserted into the index
        """
        meta = kwargs
        if self.format.get('fileinfo'):
            log.debug('Use file specific keywords from the format')
            meta = dict([(k, v) for k, v in kwargs.items()
                        if k not in self.format.get('fileinfo')])
        if not dataset:
            dataset = Dataset(**meta)

        existing_dataset = self.datasets.get(dataset.id)

        if existing_dataset and update:
            log.debug('Update existing dataset %s', existing_dataset.id)
            for key, val in meta.items():
                if getattr(existing_dataset, key):
                    existing_dataset.__setattr__(key, val)
            dataset = existing_dataset

        if not existing_dataset:
            if ',' in dataset.id:
                log.info('Gather replicates info for %s', dataset.id)
                reps = self.find_replicates(**kwargs)
                if reps:
                    dataset = reps[0].merge(reps[1:])
            self.datasets[dataset.id] = dataset
            dataset = self.datasets.get(dataset.id)
        else:
            log.debug('Use existing dataset %s', dataset.id)

        if kwargs.get('path') and kwargs.get('type'):
            log.debug('Add %s to dataset', kwargs.get('path'))
            dataset.add_file(update=update, **kwargs)

        return dataset

    def remove(self, clear=False, **kwargs):
        """Remove dataset(s) from the index given a search query.
        """
        datasets = self.select(**kwargs).datasets.keys()
        if datasets:
            log.debug('Remove datasets %s', datasets)
            for k in datasets:
                dataset = self.datasets.get(k)
                if 'path' in kwargs:
                    log.debug('Remove %s', kwargs.get('path'))
                    dataset.rm_file(path=kwargs.get('path'))
                    if len(dataset) == 0 and clear:
                        del self.datasets[k]
                else:
                    if 'id' in kwargs:
                        log.debug('Remove whole %s', dataset)
                        del self.datasets[k]
                    else:
                        log.debug('Nothing to remove for %s', kwargs)

    def save(self, path=None):
        """Save changes to the index file
        """
        if not path and self.path:
            log.debug('Use path from the Index instance')
            path = self.path
            index = open(path, 'w+')
        elif not self.path:
            index = sys.stdout
        if path != self.path:
            self.path = os.path.abspath(path)
        log.debug('Save %s', path)
        for line in self.export(map=None):
            index.write("%s%s" % (line, os.linesep))

    def export(self, absolute=False, export_type='index', tags=None,
               header=False, **kwargs):
        """Export the index file information. ``kwargs`` contains the format
        information.

        :keyword absolute: specify if absolute paths should be used. Default:
        false
        :keyword type: specify the export type. Values:
        ['index','tab','json']. Default: 'index'
        """
        import simplejson as json

        if self.format:
            log.debug('Use format from the Index instance')
            if not kwargs:
                kwargs = {}
            kwargs = dict(self.format.items() + kwargs.items())

        dsid = kwargs.pop('id')
        idxmap = kwargs.pop('map', None)
        colsep = kwargs.pop('colsep', '\t')
        #fileinfo = kwargs.pop('fileinfo', [])

        path = 'path'

        if idxmap:
            log.debug('Use correspondence table for keywords')
            for key, val in idxmap.items():
                if val:
                    idxmap[val] = key

            path = idxmap.get('path', 'path')

        out = []

        if export_type == 'tab':
            log.debug('Create header for %s export format', type)
            if not self._alltags:
                self._create_lookup()
            headline = self._alltags
            if tags:
                headline = tags
        for dataset in self.datasets.values():
            expd = dataset.export(tags=tags)
            for dic in expd:
                line = dict()
                for k, val in dic.items():
                    if k == 'id' and dsid:
                        k = dsid
                    if k == 'path' and absolute:
                        if self.path and not os.path.isabs(val):
                            val = os.path.join(os.path.dirname(self.path),
                                               os.path.normpath(val))
                    if idxmap:
                        k = idxmap.get(k,k)
                    if k:
                        line[k] = val
                log.debug('Create output for %s format', export_type)
                if export_type == 'index':
                    out.append(colsep.join([line.pop(path, '.'),
                                            to_tags(**dict(line.items() +
                                                           kwargs.items()))]))
                if export_type == 'json':
                    out.append(json.dumps(line))
                if export_type == 'tab':
                    vals = line.values()
                    if tags or len(line.values()) != len(headline):
                        vals = [line.get(l, 'NA') if l != 'id'
                                else line.get(dsid) for l in headline]
                    for i, val in enumerate(vals):
                        if type(val) == list:
                            val = quote_tags(val)
                            vals[i] = self.format.get('rep_sep', ",").join(val)
                    out.append(colsep.join(quote_tags(vals)))

        if export_type == 'tab':
            log.debug('Adjust output for %s export format', export_type)
            out = list(set(out))
            if tags:
                out.sort()
            if header:
                out = [colsep.join(headline)] + out

        return out

    def _create_lookup(self):
        """Create the index lookup table for querying the index by attribute
        values.
        """

        if self.datasets:

            log.debug('Create lookup table')

            self._lookup = {}
            if not self.format.get('fileinfo'):
                log.debug('''No information about file specific keywords
                           available''')
                self.format['fileinfo'] = []
            # keys = set(self.datasets.values()[0]._metadata.keys()).union(
            #     set(self.format.get('fileinfo')))
            #for k in keys:
            #    self._lookup[k] = {}
            for dataset in self.datasets.values():
                log.debug('Create entries for metadata')
                for k, val in dataset.get_meta_items():
                    if k in self.format.get('fileinfo'):
                        continue
                    if k == 'id':
                        k = self.format.get('id', 'id')
                    if k not in self._lookup.keys():
                        self._lookup[k] = {}
                    if type(val) == list:
                        val = ','.join(val)
                    if not self._lookup[k].get(val):
                        self._lookup[k][val] = []
                    self._lookup[k][val].append(dataset.id)
                log.debug('Create entries for files')
                self._lookup['type'] = {}
                self._lookup['path'] = {}
                self._lookup['_info'] = {}
                for key, info in [x for x in dataset._files.items()]:
                    if not self._lookup['type'].get(key):
                        self._lookup['type'][key] = []
                    self._lookup['type'][key].extend(info.keys())
                    for path, infos in info.items():
                        if not self._lookup['path'].get(path):
                            self._lookup['path'][path] = []
                        self._lookup['path'][path].append(path)
                        if not self._lookup['_info'].get(path):
                            self._lookup['_info'][path] = []
                        metadata = [(i[0], ','.join(i[1]))
                                    if type(i[1]) == list
                                    else i for i in dataset.get_meta_items()]
                        self._lookup['_info'][path].append(dict(set(metadata
                                                           + infos.items())))
                        for k, val in infos.items():
                            if k in self.format.get('fileinfo'):
                                if k not in self._lookup.keys():
                                    self._lookup[k] = {}
                                if not self._lookup[k].get(val):
                                    self._lookup[k][val] = []
                                self._lookup[k][val].append(path)

            self._alltags = [i for i in self._lookup.keys()
                             if not i.startswith('_')]

            log.debug('Lookup table created')

    def select(self, id=None, oplist=['>', '=', '<', '!'], absolute=False,
               exact=False, **kwargs):
        """Select datasets from indexfile. ``kwargs`` contains the attributes
        to be looked for.

        :keyword id: the id to select
        :keyword absolute: specify if absolute paths should be used. Default:
        false

        """

        setlist = []
        finfo = {}
        meta = False

        if not id and not kwargs:
            log.debug('No query specified')
            return self

        if id:
            log.debug('Query by id=%s', id)
            kwargs[self.format.get('id', 'id')] = id

        if kwargs:
            log.debug('Query by %s', kwargs)
            if set(kwargs.keys()).difference(set(self.format.get('fileinfo'))):
                meta = True
            if not self.datasets:
                if meta:
                    return self
                else:
                    return []
            if not self._lookup:
                self._create_lookup()
            for k, val in kwargs.items():
                if meta:
                    log.debug('Metadata query')
                    if k in self.format.get('fileinfo'):
                        finfo[k] = val
                        continue
                log.debug('File query')
                if not k in self._lookup.keys():
                    raise ValueError('''The attribute %r is not present in the
                                     index''' % k)
                if type(val) == list:
                    operator = ' in '
                    value = val
                else:
                    operator = "".join([x for x in list(val) if x in oplist])
                    while operator in ['', '=', '!']:
                        operator = '%s=' % operator
                    value = "".join([x for x in list(val) if x not in oplist])
                try:
                    value = int(value)
                    log.debug('Query integer value %d for %s', value, k)
                    query = '''[id for k, v in self._lookup[%r].items() if
                            int(k) %s%r for id in v]''' % (k, operator, value)
                except:
                    log.debug('Query string value %s for %s', value, k)
                    if exact or type(value) == list:
                        log.debug('Look for exact values')
                        search = "k%s%r" % (operator, value)
                    else:
                        value = str(value)
                        search = 're.match(%r, k)' % value
                    query = '''[id for k, v in self._lookup[%r].items() if %s
                            for id in v]''' % (k, search)

                setlist.append(set(eval(query)))

        if meta:
            log.debug('Metadata query')
            datasets = dict([(x, self.datasets.get(x)) for x in
                            set.intersection(*setlist)
                            if self.datasets.get(x)])
            i = Index(datasets=datasets, format=self.format, path=self.path)
            i._create_lookup()
        else:
            log.debug('File query')
            filelist = [x for x in set.intersection(*setlist) if "/" in x]
            if absolute:
                log.debug('Use absolute path')
                filelist = [os.path.join(os.path.dirname(self.path), x)
                            if not os.path.isabs(x) and self.path
                            else x for x in filelist]
            i = Index(format=self.format, path=self.path)
            for afile in filelist:
                for info in self._lookup['_info'].get(afile):
                    i.insert(**info)
            i._create_lookup()

        if finfo and meta:
            i = i.select(None, oplist, absolute, exact, **finfo)

        return i

    def __len__(self):
        return len(self.datasets)

    def lock(self):
        """Lock this index file

        """
        if self._lock is not None:
            log.debug('Indexfile already locked')
            return False

        if not self.path:
            log.debug('Index has no path')
            return False

        from lockfile import LockFile

        base = os.path.dirname(self.path)
        if not os.path.exists(base):
            os.makedirs(base)

        self._lock = LockFile(self.path)
        try:
            log.debug('Lock indexfile %s', self.path)
            self._lock.acquire()
            return True
        except Exception, exc:
            raise StoreException("Locking index file failed: %s" % str(exc))

    def release(self):
        """Release a lock on this index file

        """
        if self._lock is None:
            log.debug('No lock to release')
            return False
        log.debug('Release lock %s', self._lock)
        self._lock.release()
        self._lock = None
        return True

    @classmethod
    def guess_type(cls, input_file, trail=';', delimiters=None):
        """Guess type of an input file for importing data into the index.

        :param file: the input file
        :keyword trail: the trailing charachter of each key/value pair
        :keyword delimiters: the allowed fields delimiters

        """
        columns = input_file.readline().split("\t")
        if len(columns) == 2 and ';' in columns[1]:
            return "idx", None

        import csv

        if not csv.Sniffer().has_header(input_file.readline()):
            raise ValueError('Metadata input_file must have a header')
        input_file.seek(0)

        dialect = csv.Sniffer().sniff(input_file.readline(),
                                      delimiters=delimiters)
        input_file.seek(0)

        if dialect.delimiter == ',':
            log.debug('Csv input_file detected')
            return 'csv', dialect

        reader = csv.DictReader(input_file, dialect=dialect)

        if len(reader.fieldnames) < 2:
            raise ValueError('Not enough columns in metadata input_file')

        if trail in reader.fieldnames[1]:
            log.debug('Indexfile detected')
            return 'index', None

        log.debug('Tsv input_file detected')
        return 'tsv', dialect

    @classmethod
    def parse_line(cls, line, **kwargs):
        """Parse an index file line and returns a tuple with
        the path to the file referred by the line (if any) and a
        dictionary with the parsed key/value pairs. ``kwargs`` is
        used to specify the index format information.

        :param str: the line to parse

        """
        file_path = None
        tags = line

        sep = kwargs.get('sep', '=')
        trail = kwargs.get('trail', ';')
        dsid = kwargs.get('id')

        expr = '^(?P<file>.+)\t(?P<tags>.+)$'
        match = re.match(expr, line)
        if match:
            log.debug('Matched indexile line %s', line)
            file_path = match.group('file')
            tags = match.group('tags')

        tagsd = {}
        expr = '(?P<key>[^ ]+)%s\"?(?P<value>[^%s\"]*)\"?%s' % (
            sep, trail, trail)
        for match in re.finditer(expr, tags):
            key = match.group('key')
            log.debug('Matched keyword %s', key)
            if key == dsid:
                log.debug('Map id keyword %s', key)
                key = 'id'
            tagsd[key] = match.group('value')

        if not tagsd:
            log.debug('No keywords matched')
            if os.path.isfile(os.path.abspath(tags)):
                log.debug('Second column is a file')
                file_path = os.path.abspath(tags)

        tagsd['path'] = file_path

        return tagsd

    @classmethod
    def map_keys(cls, obj, **kwargs):
        """ Maps ``obj`` keys using the mapping information contained
        in the arguments. ``kwargs`` is used to specify the index format
        information.

        :param obj: the input dictionary

        """
        if not obj:
            log.debug('No data to map')
            return {}

        dsid = kwargs.get('id')
        idxmap = kwargs.get('map', {})

        out = {}
        if idxmap:
            log.debug('Mappings present')
            for k, val in idxmap.items():
                if not val:
                    idxmap.pop(k)
                    continue
                idxmap[val] = k

        log.debug('Create output dictionary')
        for k, val in obj.items():
            key = k
            if map:
                log.debug('Map %s to %s', key, idxmap.get(key))
                key = idxmap.get(k)
            if key:
                if key == dsid:
                    key = "id"
                out[key] = val
        return out
