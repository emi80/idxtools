"""Index module.

The module provide classes to perform operations on index files.

"""
import re
import io
import os
import sys
import csv
import yaml
import hashlib
import tempfile
import indexfile
import simplejson as json
from copy import deepcopy
from lockfile import LockFile
from . import utils
from .config import config, OUTPUT_FORMATS
from .dataset import Dataset

# setup logger
log = indexfile.get_logger(__name__)


# module functions
def map_keys(obj, map_only=False):
    """ Maps ``obj`` keys using the mapping information contained
    in the arguments. ``kwargs`` is used to specify the index format
    information.

    :param obj: the input dictionary

    """
    # TODO: use map_keys as a general function for mapping
    if not obj:
        log.debug('No data to map')
        return {}

    out = deepcopy(obj)
    if config.map:
        log.debug('Mapping attribute names using map: %s', config.map)
        if map_only:
            # use known attributes with non-empty mapping
            log.debug("Using only known mappings from the map")
            out = dict([(config.map.get(k), v) for (k, v) in out.iteritems()
                       if config.map.get(k)])
            # if not dsid in out:
            #     out[dsid] = obj[dsid]
        else:
            log.debug("Using input attributes if no mapping found")
            out = dict([(config.map.get(k), v) if config.map.get(k)
                       else (k, v) for (k, v) in out.iteritems()])

    return out


def to_str(addons=None, quote=None, **kwargs):
    """Convert a dictionary to a string in index file format"""
    taglist = []
    for key, val in dict(sorted(kwargs.items(), key=lambda k: k[0])).items():
        if addons and key in addons:
            continue
        if type(val) == list:
            val = config.format.rep_sep.join([
                utils.quote([key, value])[1] for value in val])
        else:
            val = str(val)
            key, val = utils.quote([key, val])
        taglist.append('%s%s%s%s' % (key, config.format.kw_sep, val, config.format.kw_trail))
    return config.format.tag_sep.join(sorted(taglist))


def guess_type(input_file, delimiters=None):
    """Guess type of an input file for importing data into the index.

    :param file: the input file
    :keyword trail: the trailing charachter of each key/value pair
    :keyword delimiters: the allowed fields delimiters

    """
    columns = input_file.readline().split("\t")
    if len(columns) == 2 and config.format.kw_trail in columns[1]:
        return "index", None

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

    if config.format.kw_trail in reader.fieldnames[1]:
        log.debug('Indexfile detected')
        return 'index', None

    log.debug('Tsv input_file detected')
    return 'tsv', dialect

def parse_line(line):
    """Parse an index file line and returns a tuple with
    the path to the file referred by the line (if any) and a
    dictionary with the parsed key/value pairs. ``kwargs`` is
    used to specify the index format information.

    :param str: the line to parse

    """

    col = config.format.col_sep
    trail = config.format.kw_trail
    sep = config.format.kw_sep
    pd = config.path_desc

    file_path, meta = line.strip().split(col)

    def kws():
        for item in meta[:-1].strip().split(trail):
            key, value = item.strip().split(sep)
            yield (key, value)

    tags = dict(kws())
    tags[pd] = file_path

    return tags


class Index(object):
    """A class to access information stored into 'index files'.
    """

    def __init__(self, fp=None, datasets=None):
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
        self.fp = fp

        self.datasets = datasets or {}
        self._lock = None
        self._lookup = {}
        self._alltags = []

        if self.fp:
            self.load()

    def load(self):
        """Load/import data into the index
        """
        if self.datasets:
            log.debug("Overwrite exisitng data")
            del self.datasets
            self.datasets = {}

        log.debug('Load from %s', self.fp)
        index_file = self.get_seekable_stream()

        log.debug('Compute index checksum')
        self.hash = self.check_sum(force=True)
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
            tags = parse_line(line)
            if config.format.rep_sep in tags[config.id_desc]:
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
        idxmap = config.get('map', {})
        if import_format and not idxmap:
            config.format['map'] = idxmap
            for key in reader.fieldnames:
                if not key in idxmap:
                    idxmap[key] = key
            yaml.dump(config.format, open(format_file, 'w'), default_flow_style=False)

        for line in reader:
            tags = map_keys(line, config.map_only)
            dataset = self.insert(**tags)

    def is_seekable(self):
        """Check if the underlying stream is seekable
        """
        if not self.fp:
            return False
        try:
            self.fp.seek(0)
        except IOError as e:
            if e.message == "underlying stream is not seekable":
                return False
            else:
                raise e
        return True

    def get_seekable_stream(self):
        """Return a seekable stream of the index file. Creates a temporary
        file if the original stream is not seekable.
        """
        if self.is_seekable():
            self.fp.seek(0)
            return self.fp
        else:
            log.debug('Create temporary file for %s', self.fp.name)
            index_file = tempfile.TemporaryFile()
            for line in self.fp:
                index_file.write("%s" % line)
            index_file.seek(0)
            return index_file

    def check_sum(self, algorithm='md5', force=False):
        """Return the hash of the index file or compute it using :algorithm:"""
        if not self.fp:
            raise AttributeError('No path specified')
        if force:
            hasher = hashlib.new(algorithm)
            for line in self.get_seekable_stream():
                hasher.update(line)
            self.hash = hasher.hexdigest()
        return self.hash

    def insert(self, update=False, addkeys=False, dataset=None, **kwargs):
        """Add a dataset to the index. Keyword arguments contains the dataset
        attributes.

        :keyword update: specifies whether existing values has to be updated
        :keyword dataset: the :class:`Dataset` to be inserted into the index
        """
        empty_paths = [None, '', '.']

        meta = kwargs
        if config.fileinfo:
            log.debug('Use file specific keywords from the format')
            meta = dict([(k, v) for k, v in kwargs.items()
                        if k not in config.fileinfo])

        dsid = kwargs.get(config.id_desc) or kwargs.get('id')

        existing_dataset = self.datasets.get(dsid)

        if existing_dataset is not None:
            log.debug('Use existing dataset %s', existing_dataset.id)
            if update:
                log.debug('Update existing dataset %s', existing_dataset.id)
                for key, val in meta.items():
                    if addkeys or getattr(existing_dataset, key):
                        existing_dataset.__setattr__(key, val)
            dataset = existing_dataset
        else:
            dataset = Dataset(**meta)
            if config.format.rep_sep in dataset.id:
                log.info('Gather replicates info for %s', dataset.id)
                reps = self.find_replicates(**kwargs)
                if reps:
                    dataset = reps[0].merge(reps[1:])
            self.datasets[dataset.id] = dataset
            dataset = self.datasets.get(dataset.id)

        if kwargs.get(config.path_desc) not in empty_paths:
            log.debug('Add %s to dataset', kwargs.get(config.path_desc))
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
                fileinfo = config.fileinfo
                if any([tag in fileinfo for tag in kwargs]):
                    rmargs = dict((tag, kwargs[tag]) for k in kwargs if k in fileinfo)
                    log.debug('Remove %s', rmargs)
                    dataset.rm_file(**rmargs)
                    if len(dataset) == 0 and clear:
                        del self.datasets[k]
                else:
                    if config.id_desc in kwargs:
                        log.debug('Remove whole %s', dataset)
                        del self.datasets[k]
                    else:
                        log.debug('Nothing to remove for %s', kwargs)

    def save(self):
        """Save changes to the index file
        """
        log.debug('Save index to %s', self.fp.name)
        with open(self.fp.name, 'w') as index:
            for line in self.export(ignore_map=True):
                index.write("%s%s" % (line, os.linesep))

    def all_tags(self):
        """Return the list of all attributes in the index"""
        keys = [i for d in self.datasets.values() for i in d.export()]
        def union(x, y):
            return set.union(set(x), set(y))
        return list(reduce(union, keys))


    def export(self, absolute=False, output_format='index', tags=None,
               header=False, hide_missing=False, map_keys=False, **kwargs):
        """Export the index file information. ``kwargs`` contains the format
        information.

        :keyword absolute: specify if absolute paths should be used. Default:
        false
        :keyword type: specify the export type. Values:
        {0}. Default: 'index'
        """.format(OUTPUT_FORMATS)

        if isinstance(tags, str):
            tags=[tags]

        sort_by = None
        if config.format:
            log.debug('Use format from the Index instance')
            if not kwargs:
                kwargs = {}
            kwargs = dict(config.format.items() + kwargs.items())

        dsid = kwargs.pop('id', 'id')
        idxmap = kwargs.pop('map', None)
        colsep = OUTPUT_FORMATS.get(output_format, {}).get('colsep','\t')
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
                        if self.fp and not os.path.isabs(val):
                            val = os.path.join(os.path.dirname(self.fp),
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

        log.debug('Create output for %s format', output_format)
        out = []
        if output_format == 'index':
            for line in dsets:
                if hide_missing and not line.get(path):
                    continue
                out.append(colsep.join([line.pop(path, '.'),
                           to_str(**dict(line.items()
                           ))]))

        if output_format == 'json':
            out.append(json.dumps(dsets, indent=4))

        if output_format == 'yaml':
            out.append(yaml.dump(dsets, indent=4, default_flow_style=False))

        if output_format == 'tsv' or output_format == 'csv':
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
                kwargs[config.id_desc] = kwargs.pop('id')
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

    def find_replicates(self, **kwargs):
        """Try to find replicates in the index using a dataset id made from
        the concatenation of multiple dataset ids
        """
        if 'id' in kwargs:
            kwargs[config.id_desc] = kwargs.pop('id')
        if not kwargs.get(config.id_desc):
            return None
        ids = kwargs.get(config.id_desc).split(config.format.rep_sep)
        datasets = dict([
            (k, self.datasets[k]) for k in ids if k in self.datasets])
        if not datasets:
            return None
        if len(datasets) != len(ids):
            raise ValueError('Some of the ids for the replicate do not exist. \
                Please check the dataset ids')
        return [datasets[k] for k in sorted(datasets.keys())]

    def __len__(self):
        return len(self.datasets)

    def __setattr__(self, name, value):
        if name == 'fp':
            if isinstance(value, str):
                value = open(value, 'r')

        super(Index, self).__setattr__(name, value)

    def lock(self):
        """Lock this index file

        """
        if self._lock is not None:
            log.debug('Indexfile already locked')
            return False

        if not self.fp:
            log.debug('Index has no path')
            return False

        base = os.path.dirname(self.fp)
        if not os.path.exists(base):
            os.makedirs(base)

        self._lock = LockFile(self.fp)
        try:
            log.debug('Lock indexfile %s', self.fp)
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
