"""Index module.

The module provide classes to perform operations on index files.

"""
import re
import io
import os
import sys
import csv
import yaml
import tempfile
import indexfile
import simplejson as json
from copy import deepcopy
from lockfile import LockFile
from . import utils
from .config import config, OUTPUT_FORMATS
from .dataset import Dataset

# setup logger
log = indexfile.getLogger(__name__)


# module functions
def map_keys(obj, map_only=False, **kwargs):
    """ Maps ``obj`` keys using the mapping information contained
    in the arguments. ``kwargs`` is used to specify the index format
    information.

    :param obj: the input dictionary

    """
    # TODO: use map_keys as a general function for mapping
    if not obj:
        log.debug('No data to map')
        return {}

    dsid = kwargs.get('id', 'id')
    idxmap = kwargs.get('map', {})

    # return original dict if no id and map definitions are found
    if not idxmap and not dsid:
        return obj

    out = dict(obj.items())
    if idxmap:
        log.debug('Mapping attribute names using map: %s', idxmap)
        if map_only:
            # use known attributes with non-empty mapping
            log.debug("Using only known mappings from the map")
            out = dict([(idxmap.get(k), v) for (k, v) in out.iteritems()
                       if idxmap.get(k)])
            if not dsid in out:
                out[dsid] = obj[dsid]
        else:
            log.debug("Using input attributes if no mapping found")
            out = dict([(idxmap.get(k), v) if idxmap.get(k)
                       else (k, v) for (k, v) in out.iteritems()])

    return out


def to_str(kw_sep=' ', sep='=', trail=';', rep_sep=',', addons=None, quote=None, **kwargs):
    """Convert a dictionary to a string in index file format"""
    taglist = []
    for key, val in dict(sorted(kwargs.items(), key=lambda k: k[0])).items():
        if addons and key in addons:
            continue
        if type(val) == list:
            val = rep_sep.join([
                utils.quote([key, value])[1] for value in val])
        else:
            val = str(val)
            key, val = utils.quote([key, val])
        taglist.append('%s%s%s%s' % (key, sep, val, trail))
    return kw_sep.join(sorted(taglist))


def guess_type(input_file, trail=';', delimiters=None):
    """Guess type of an input file for importing data into the index.

    :param file: the input file
    :keyword trail: the trailing charachter of each key/value pair
    :keyword delimiters: the allowed fields delimiters

    """
    columns = input_file.readline().split("\t")
    if len(columns) == 2 and ';' in columns[1]:
        return "idx", None

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


def parse_line(line, **kwargs):
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
        tagsd[key] = match.group('value')

    if not tagsd:
        log.debug('No keywords matched')
        if os.path.isfile(os.path.abspath(tags)):
            log.debug('Second column is a file')
            file_path = os.path.abspath(tags)

    tagsd['path'] = file_path

    return tagsd



class Index(object):
    """A class to access information stored into 'index files'.
    """

    def __init__(self, path=None, format=None, datasets=None):
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

        if isinstance(path, str):
            path = os.path.abspath(path)

        self.path = path

        self.datasets = datasets or {}
        self._lock = None
        self._lookup = {}
        self._alltags = []

        if path and format:
            self.open()

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
    def seekable(self):
        if not self.path:
            return False
        index_file = self.path
        if not hasattr(index_file, 'seek'):
            index_file = open(index_file, 'r')
        try:
            index_file.seek(0)
        except IOError as e:
            if e.message == "underlying stream is not seekable":
                return False
            else:
                raise e
        return True

    def _open_file(self, index_file):
        """Open index file"""

        if self.datasets:
            log.debug("Overwrite exisitng data")
            input_format = indexfile.default_format
            del self.datasets
            self.datasets = {}
        if index_file == sys.stdin:
            log.debug('Create temporary file for %s', index_file)
            index_file = tempfile.TemporaryFile()
            for line in sys.stdin:
                index_file.write("%s" % line)
            index_file.seek(0)
        log.debug('Guess file format')
        dummy_file_type, dialect = guess_type(index_file)
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
        replicates = []
        for line in index_file:
            tags = parse_line(line, **config.format)
            if config.format.get('rep_sep') in tags[config.format.get('id', 'id')]:
                # postpone inserting replicates lines
                replicates.append(tags)
            else:
                dataset = self.insert(**tags)
        for tags in replicates:
            dataset = self.insert(**tags)

    def _load_table(self, index_file, dialect=None):
        """Import entries from a SV file. The sv file must have an header line
        with the name of the attributes.

        :param index_file: a :class:`file` object pointing to the input file
        :keyword dialect: a :class:`csv.dialect` containg the input file
        format information

        """
        reader = csv.DictReader(index_file, dialect=dialect)

        format_file = 'imported_format.yml'
        import_format = not os.path.exists(format_file)
        idxmap = config.format.get('map', {})
        if import_format and not idxmap:
            config.format['map'] = idxmap
            for key in reader.fieldnames:
                if not key in idxmap:
                    idxmap[key] = key
            yaml.dump(config.format, open(format_file, 'w'), default_flow_style=False)

        for line in reader:
            tags = map_keys(line, config.map_only, **config.format)
            dataset = self.insert(**tags)

    def find_replicates(self, **kwargs):
        """Try to find replicates in the index using a dataset id made from
        the concatenation of multiple dataset ids
        """
        dsid = self.format.get('id', 'id')
        if 'id' in kwargs:
            kwargs[dsid] = kwargs.pop('id')
        if not kwargs.get(dsid):
            return None
        ids = kwargs.get(dsid).split(',')
        datasets = dict([
            (k, self.datasets[k]) for k in ids if k in self.datasets])
        if not datasets:
            return []
        if len(datasets) != len(ids):
            raise ValueError('Some of the ids for the replicate do not exist. \
                Please check the dataset ids')
        return [datasets[k] for k in sorted(datasets.keys())]

    def insert(self, update=False, addkeys=False, dataset=None, **kwargs):
        """Add a dataset to the index. Keyword arguments contains the dataset
        attributes.

        :keyword update: specifies whether existing values has to be updated
        :keyword dataset: the :class:`Dataset` to be inserted into the index
        """
        empty_paths = [None, '', '.']

        dsid = config.format.get('id', 'id')

        if 'id' in kwargs:
            kwargs[dsid] = kwargs.pop('id')

        meta = kwargs
        config.format.fileinfo = config.format.get('fileinfo')
        if config.format.get('fileinfo'):
            log.debug('Use file specific keywords from the format')
            meta = dict([(k, v) for k, v in kwargs.items()
                        if k not in config.format.get('fileinfo')])
        if not dataset:
            dataset = Dataset(**meta)

        existing_dataset = self.datasets.get(getattr(dataset, dsid))

        if existing_dataset is not None:
            if update:
                log.debug('Update existing dataset %s', getattr(existing_dataset, dsid))
                for key, val in meta.items():
                    if addkeys or getattr(existing_dataset, key):
                        existing_dataset.__setattr__(key, val)
            dataset = existing_dataset

        if existing_dataset is None:
            if ',' in getattr(dataset, dsid):
                log.info('Gather replicates info for %s', getattr(dataset, dsid))
                reps = self.find_replicates(**kwargs)
                if reps:
                    dataset = reps[0].merge(reps[1:], dsid=dsid)
            self.datasets[getattr(dataset, dsid)] = dataset
            dataset = self.datasets.get(getattr(dataset, dsid))
        else:
            log.debug('Use existing dataset %s', getattr(dataset, dsid))

        if kwargs.get('path') not in empty_paths:
        #if os.path.isfile(kwargs.get('path')):
            log.debug('Add %s to dataset', kwargs.get('path'))
            dataset.add_file(update=update, **kwargs)

        return dataset

    def remove(self, clear=False, **kwargs):
        """Remove dataset(s) from the index given a search query.
        """

        dsid = config.format.get('id', 'id')

        if 'id' in kwargs:
            kwargs[dsid] = kwargs.pop('id')

        datasets = self.lookup(**kwargs).datasets.keys()
        if datasets:
            log.debug('Remove datasets %s', datasets)
            for k in datasets:
                dataset = self.datasets.get(k)
                fileinfo = config.format.get('fileinfo')
                if any([tag in fileinfo for tag in kwargs]):
                    rmargs = dict((tag, kwargs[tag]) for k in kwargs if k in fileinfo)
                    log.debug('Remove %s', rmargs)
                    dataset.rm_file(**rmargs)
                    if len(dataset) == 0 and clear:
                        del self.datasets[k]
                else:
                    if dsid in kwargs:
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

    def all_tags(self):
        """Return the list of all attributes in the index"""
        keys = [i for d in self.datasets.values() for i in d.export()]
        def union(x, y):
            return set.union(set(x), set(y))
        return list(reduce(union, keys))


    def export(self, absolute=False, output_format='index', tags=None,
               header=False, hide_missing=False, **kwargs):
        """Export the index file information. ``kwargs`` contains the format
        information.

        :keyword absolute: specify if absolute paths should be used. Default:
        false
        :keyword type: specify the export type. Values:
        ['index','tab','json']. Default: 'index'
        """
        sort_by = None
        if self.format:
            log.debug('Use format from the Index instance')
            if not kwargs:
                kwargs = {}
            kwargs = dict(self.format.items() + kwargs.items())

        dsid = kwargs.pop('id', 'id')
        idxmap = kwargs.pop('map', None)
        colsep = kwargs.pop('colsep', '\t')
        fileinfo = kwargs.pop('fileinfo', [])

        path = 'path'

        if tags:
            tags = [tag if tag != 'id' else dsid for tag in tags]
            tags = [t.replace('{id}','{'+ dsid + '}') for t in tags]
            sort_by = tags

        if idxmap:
            log.debug('Use correspondence table for keywords')
            for key, val in idxmap.items():
                if val:
                    idxmap[val] = key

            path = idxmap.get('path', 'path')

        dsets = []

        for dataset in self.datasets.values():
            for ak, addon in config.format.get('addons', {}).items(): # addon ~ 'data_type'
                mapping = addon.get('mapping') # 'view'
                if mapping:
                    for k, v in dataset:
                        if v.get(mapping) in addon:
                            v[ak] = addon.get(v.get(mapping))
            expd = dataset.export(tags=tags)
            for dic in expd:
                line = dict()
                for k, val in dic.items():
                    if k == 'path' and absolute:
                        if self.path and not os.path.isabs(val):
                            val = os.path.join(os.path.dirname(self.path),
                                               os.path.normpath(val))
                    if idxmap:
                        k = idxmap.get(k, k)
                    if k:
                        line[k] = val
                dsets.append(line)

        # default sort datasets by path if no tags specified
        if not sort_by:
            sort_by = [path]

        # sort datasets
        dsets.sort(key=lambda x: [x.get(tag) for tag in sort_by])

        log.debug('Create output for %s format', export_type)
        out = []
        if export_type == 'index':
            for line in dsets:
                if hide_missing and not line.get(path):
                    continue
                out.append(colsep.join([line.pop(path, '.'),
                           to_str(**dict(line.items()
                           ))]))

        if export_type == 'json':
            for line in dsets:
                out.append(json.dumps(line))

        if export_type == 'tab':
            headline = []
            if tags:
                headline = [tag if tag != 'id' else dsid for tag in tags]
            else:
                keys = [d.keys() for d in dsets]
                def union(x, y):
                    return set.union(set(x), set(y))
                headline = list(reduce(union, keys))
            def sort_header(x):
                if not tags:
                    return x
                if tags and x in tags:
                    return tags.index(x)
                return sys.maxint

            headline.sort(key=sort_header)
            for line in dsets:
                vals = [line.get(k, 'NA') for k in headline]
                if tags or len(line.values()) != len(headline):
                    vals = [line.get(l, 'NA') for l in headline]
                for i, val in enumerate(vals):
                    if hide_missing and val == "NA":
                        break
                    if type(val) == list:
                        val = utils.quote(val)
                        vals[i] = config.format.get('rep_sep', ",").join(val)
                else:
                    if colsep.join(utils.quote(vals)) not in out:
                        out.append(colsep.join(utils.quote(vals)))
            if header:
                out.insert(0, colsep.join(headline))

        return out

    def lookup(self, exact=False, or_query=False, **kwargs):
        """Select datasets from indexfile. ``kwargs`` contains the attributes
        to be looked for.

        :keyword exact: exact matching of values
        :keyword or_query: specifies if an OR operator should be used for multiple attributes
                           Default: false

        """

        if not kwargs:
            log.debug('No query specified')
            return self

        if kwargs:
            if 'id' in kwargs:
                kwargs[config.format.get('id', 'id')] = kwargs.pop('id')
            log.debug('Query by %s', kwargs)
            if not self.datasets:
                return self
            datasets = {}
            for dsetk in self.datasets:
                dset = self.datasets.get(dsetk)
                if or_query:
                    for key, val in kwargs.items():
                        if {key: val, 'exact': exact} in dset:
                            obj = dset.dice(exact=exact, **{key: val})
                            if obj:
                                datasets[dsetk] = obj
                            else:
                                datasets[dsetk] = dset
                kwargs['exact'] = exact
                if kwargs in dset:
                    obj = dset.dice(exact=exact, **kwargs)
                    if obj:
                        datasets[dsetk] = obj
                    else:
                        datasets[dsetk] = dset
            return Index(datasets=datasets)

        return None

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