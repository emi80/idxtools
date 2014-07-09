"""Index module.

The module provide classes to perform operations on index files.

"""
import re
import os
import sys
import csv
import simplejson as json
import tempfile
import simplejson as json
from lockfile import LockFile
from copy import deepcopy
from indexfile.utils import *
from copy import copy, deepcopy
from indexfile.dataset import Dataset

# setup logger
import indexfile
# Disable warning about invalid constant name
# pylint: disable=C0103
log = indexfile.getLogger(__name__)
# pylint: enable=C0103


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

        The format information can be expressed with a dictionary as followsclone:

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

    def set_format(self, input_format=None):
        """Set index format from json string or file

        :param str: the input string. It can be a path to a file or a valid
        json string.

        """

        if not input_format:
            log.debug('Use default indexfile format')
            input_format = indexfile.default_format
            return

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

        if existing_dataset:
            if update:
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
        datasets = self.lookup(**kwargs).datasets.keys()
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
               header=False, hide_missing=False, **kwargs):
        """Export the index file information. ``kwargs`` contains the format
        information.

        :keyword absolute: specify if absolute paths should be used. Default:
        false
        :keyword type: specify the export type. Values:
        ['index','tab','json']. Default: 'index'
        """

        if self.format:
            log.debug('Use format from the Index instance')
            if not kwargs:
                kwargs = {}
            kwargs = dict(self.format.items() + kwargs.items())

        dsid = kwargs.pop('id', None)
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
            # if not self._alltags:
            #     self._alltags = self.datasets.values()[0]._metadata.keys() + self.datasets.values()[0]._files.values()[0].keys() + ['path']
            headline = []
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
                    if hide_missing and not line.get(path):
                        continue
                    out.append(colsep.join([line.pop(path, '.'),
                                            to_tags(**dict(line.items() +
                                                           kwargs.items()))]))
                if export_type == 'json':
                    out.append(json.dumps(line))
                if export_type == 'tab':
                    if not headline:
                        headline = sorted(line.keys())
                    if not tags:
                        headline = sorted(list(set.intersection(set(headline), set(line.keys()))))
                    vals = [line.get(k,'NA') for k in headline]
                    if tags or len(line.values()) != len(headline):
                        vals = [line.get(l, 'NA') if l != 'id'
                                else line.get(dsid) for l in headline]
                    for i, val in enumerate(vals):
                        if hide_missing and val == "NA":
                            break
                        if type(val) == list:
                            val = quote_tags(val)
                            vals[i] = self.format.get('rep_sep', ",").join(val)
                    else:
                        out.append(colsep.join(quote_tags(vals)))

        if export_type == 'tab':
            log.debug('Adjust output for %s export format', export_type)
            out = list(set(out))
            if tags:
                out.sort()
            if header:
                out = [colsep.join(headline)] + out

        return out

    def lookup(self, exact=False, or_query=False, **kwargs):
        """Select datasets from indexfile. ``kwargs`` contains the attributes
        to be looked for.

        :keyword id: the id to select
        :keyword absolute: specify if absolute paths should be used. Default:
        false

        """

        if not id and not kwargs:
            log.debug('No query specified')
            return self

        if kwargs:
            log.debug('Query by %s', kwargs)
            if not self.datasets:
                return self
            datasets = {}
            for dsetk in self.datasets:
                dset = self.datasets.get(dsetk)
                if or_query:
                    for key, val in kwargs.items():
                        if {key: val, 'exact': exact} in dset:
                            obj = dset.get(exact=exact, **{key: val})
                            if obj:
                                datasets[dsetk] = obj
                            else:
                                datasets[dsetk] = dset
                kwargs['exact'] = exact
                if kwargs in dset:
                    obj = dset.get(exact=exact, **kwargs)
                    if obj:
                        datasets[dsetk] = obj
                    else:
                        datasets[dsetk] = dset
            return Index(datasets=datasets, format=self.format)

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
