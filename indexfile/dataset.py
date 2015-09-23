import os
import sys
import indexfile
import simplejson as json
from copy import deepcopy
from . import utils
from .config import config

# setup logger
log = indexfile.get_logger(__name__)

class Dataset(dict):
    """A class that represent a dataset in the index file.

    Each entry is identified by a dataset id (eg. labExpId) and has metadata
    information as long as file information.
    """

    def __init__(self, **kwargs):
        """Create an instance of a Dataset. ``kwargs`` contains
        the dataset metadata.

        """
        self.__dict__['_metadata'] = utils.DotDict()
        self.__dict__['_files'] = utils.DotDict()
        self.__dict__['_callbacks'] = utils.DotDict()

        for key, val in kwargs.iteritems():
            self.__setattr__(key, val)

        if config.path_desc in kwargs:
            self.add_file(**kwargs)

    def add_file(self, check_exists=False, update=False, **kwargs):
        """Add a file to the dataset files dictionary. ``kwargs`` contains
        the file information. The 'path' argument is mandatory in order
        to add the file.
        """

        path = kwargs.get(config.path_desc, None)
        if not path:
            log.debug('No path specified. Skipping')
            return

        if path in self._files and not update:
            log.debug("Skip existing %s entry", path)
            return

        if check_exists and not os.path.exists(path):
            raise IOError("File {} not found".format(path))

        if not path in self._files:
            self._files[path] = {}

        if not config.type_desc in kwargs:
            kwargs[config.type_desc] = utils.get_file_type(path)

        for key in config.fileinfo:
            if not key in kwargs:
                continue
            val = kwargs.get(key)
            if not val:
                log.debug('%s - replace missing value with NA', key)
                val = config.missing_value
            self._files[path][key] = val

    def rm_file(self, **kwargs):
        """Remove a file form the dataset files dictionary. ``kwargs`` contains
        the file information to be matched for the deletion.
        """

        path = kwargs.get(config.path_desc, None)

        if not path and not kwargs:
            log.debug('No file path neither file information specified')
            return

        if path and path in self._files:
            log.debug('Delete file entry: %s', path)
            del self[path]
            return

        result = self.dice(**kwargs)

        for k, v in result:
            del self[k]


    def export(self, types=None, tags=None):
        """Export a :class:Dataset object to a list of dictionaries (one for
        each file).

        :keyword types: the list of file types to be exported. If set only the
        file types in the list are exported. Default: None (all types
        exported).

        :keyword tags: the list of tags to be exported. If set only the
        sepcified tags will be put on output. Default: None (all tags exported)
        """
        out = []
        if not tags:
            tags = set(self.keys() + list(config.fileinfo))
        templates = [t for t in tags if '{' in t]
        if not types:
            types = set([v.type for v in self._files.values()])
        if type(types) == str:
            types = [types]
        if type(tags) == str:
            tags = [tags]
        if not self:
            log.debug('No files found in the index. Write metadata index')
            return [dict([(k, v) for k, v in self._metadata.items()
                    if k in tags])]
        for path, info in self.iterfiles(types=types):
            log.debug('Export file item: %r', path)
            data = info.copy()
            for t in templates:
                data = utils.render(data, t)
            for k in set(data.keys()).difference(tags):
                del data[k]
            out.append(data)
        return out


    def merge(self, datasets, sep=',', dsid='id'):
        """Merge metadata of this dataset with the ones from another dataset

        :param datasets: A list of datasets to be merged with the current
        dataset
        """
        if type(datasets) != list and hasattr(datasets, dsid):
            datasets = [datasets]
        mdsid = sep.join([getattr(self, dsid)] + [getattr(d, dsid) for d in datasets])
        meta = {}
        for k in set(self._metadata.keys() + [
                j for d1 in datasets for j in d1.keys()]):
            vals = [self._metadata.get(k)] + [
                getattr(d, k) for d in datasets]
            meta[k] = vals if len(set(vals)) > 1 else vals[0]
        meta[dsid] = mdsid
        d = Dataset(**meta)
        return d

    def dice(self, *args, **kwargs):
        """Returns a clone of the dataset if:
        - it contains the key-value pairs specified in kwargs
        OR
        - it contains a file specified in args
        """

        if args and len(args) == 1:
            return self.clone(args[0])
        if not kwargs:
            return Dataset()
        exact = kwargs.pop('exact', False)
        files = []
        for k, v in kwargs.items():
            if k in self._metadata:
                continue
            if k == config.path_desc and v in self._files:
                path = [v]
            else:
                path = [key for key, value in self._files.items()
                        if utils.match(v, value.get(k), exact=exact)]
            if not path:
                return Dataset()
            files.append(set(path))
        if not files:
            return Dataset()
        return self.clone(list(set.intersection(*files)))

    def clone(self, paths=None):
        """Return a copy of the datasets"""
        metadata = self._metadata
        files = self._files
        if paths:
            files = dict([(key, self._files[key]) for key in self._files
                          if key in paths])
        new_ds = deepcopy(self)
        new_ds.__dict__['_metadata'] = deepcopy(metadata)
        new_ds.__dict__['_files'] = deepcopy(files)

        return new_ds

    def keys(self):
        """Return metadata tags"""
        return self._metadata.keys()

    def items(self):
        """Return metadata items"""
        return self._metadata.items()

    def iteritems(self):
        """Return an iterator on metadata items"""
        return self._metadata.iteritems()

    def iterfiles(self, types=None):
        """Return an iterator on all files in dataset. Adds also metadata items"""
        for path, info in self._files.items():
            if not types or (types and info.type in types):
                all_info = utils.DotDict(self.items() + info.items())
                yield (path, all_info)

    @property
    def id(self):
        return self[config.id_desc]

    def get(self, name, default=None):
        try:
            return getattr(self, name)
        except:
            return default

    def __getattr__(self, name):
        if name in self._metadata.keys():
            return self._metadata.get(name)
        elif name in self._files.keys():
            return self._files.get(name)
        elif name in self._callbacks.keys():
            return self._callbacks.get(name)(self)
        files = []
        for k, v in self:
            if name in v.values():
                files.append((k, v))
        if files:
            return files
        raise AttributeError('%r object has no attribute %r' % (
            self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in config.fileinfo:
            return
        val = value or config.missing_value
        if hasattr(value, '__call__'):
            self.__dict__['_callbacks'][name] = val
        else:
            self.__dict__['_metadata'][name] = val

    def __delattr__(self, name):
        if name in self.__dict__['_metadata']:
            del self.__dict__['_metadata'][name]
        elif name in self.__dict__['_files']:
            del self.__dict__['_files'][name]
        elif name in self.__dict__['_callbacks']:
            del self.__dict__['_callbacks'][name]
        else:
            for k, v in self:
                if name in v.values():
                    del self[k]


    def __repr__(self):
        return "(Dataset {0})".format(self.id)

    def __str__(self):
        return str(self.export())

    def __iter__(self):
        """
        Iterates over all files in a dataset. Returns a tuple containing the
        path and a dictionary with the file information.
        """
        for path, info in self.iterfiles():
            yield (path, info)

    def __len__(self):
        return len(self.__dict__['_files'])

    def __nonzero__(self):
        return bool(self.__dict__['_files'])

    def __contains__(self, item):
        """Returns True if the dataset contains the key-value pairs
        specified as kwargs.
        """
        if not isinstance(item, dict):
            return False

        vals = None
        exact = item.pop('exact', False)
        match_all = item.pop('match_all', False)

        for k,v in item.items():
            if k in self.keys():
                vals = self[k]
            if k in config.fileinfo:
                vals = [info.get(k) for _, info in self.iterfiles()]
            if not vals or not utils.match(v, vals, exact=exact, match_all=match_all):
                return False

        else:
            return True

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__
