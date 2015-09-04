import os
import sys
import indexfile
import simplejson as json
from copy import deepcopy
from . import utils
from .config import config

# setup logger
log = indexfile.getLogger(__name__)

class Dataset(dict):
    """A class that represent dataset in the index file.

    Each entry is identified by a dataset id (eg. labExpId) and has metadata
    information as long as file information.
    """

    def __init__(self, **kwargs):
        """Create an instance of a Dataset. ``kwargs`` contains
        the dataset metadata.

        """
        self.__dict__['_metadata'] = utils.DotDict()
        self.__dict__['_files'] = utils.DotDict()
        self.__dict__['_attributes'] = {}


        is_file = False

        for key, val in kwargs.items():
            if key in config.fileinfo:
                is_file = True
            self.__setattr__(key, val)

        if is_file:
            self.add_file(**kwargs)

    def add_file(self, check_exists=False, update=False, **kwargs):
        """Add a file to the dataset files dictionary. ``kwargs`` contains
        the file information. The 'path' argument is mandatory in order
        to add the file.
        """

        path = kwargs.get('path', None)
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

        if not 'type' in kwargs: 
            kwargs['type'] = utils.get_file_type(path)

        for key, val in kwargs.items():
            if key not in config.fileinfo:
                continue
            if not val:
                log.debug('%s - replace missing value with NA', key)
                val = 'NA'
            self._files[path][key] = val           

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
            log.debug('Delete entry for %s', path)
            if path in self._files:
                del self._files[path]
        else:
            log.debug('Delete all %r entries', type)
            for f in [k for k,v in self._files.items()
                         if v.type == type]:
                del self._files[f]

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
                tags.extend([k for v in self._files.values()
                             for k in v.keys()])
            tags = list(set(tags))
        templates = [t for t in tags if '{' in t]
        if not types:
            types = set([v.type for v in self._files.values()])
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
        for path, info in self._files.items():
            if info.type in types:
                log.debug('Export type %r', info.type)
                items = self._metadata.items() + {'path': path, 'type': info.type}.items() + info.items()
                data = dict(items)
                for t in templates:
                    data = utils.map_path(data, t)
                data = dict([(k, v) for k, v in data.items() if k in tags])

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
                j for d1 in datasets for j in d1.get_meta_tags()]):
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
            return None
        exact = kwargs.pop('exact', False)
        files = []
        for k, v in kwargs.items():
            if k in self._metadata:
                continue
            if k == 'path' and v in self._files:
                path = [v]
            else:
                path = [key for key, value in self._files.items()
                        if utils.match(v, value.get(k), exact=exact)]
            if not path:
                return None
            files.append(set(path))
        if not files:
            return None
        return self.clone(list(set.intersection(*files)))

    def clone(self, paths=None):
        """Return a copy of the datasets"""
        metadata = self._metadata
        files = self._files
        attrs = self._attributes
        if paths:
            files = dict([(key, self._files[key]) for key in self._files
                          if key in paths])
        new_ds = deepcopy(self)
        new_ds.__dict__['_metadata'] = deepcopy(metadata)
        new_ds.__dict__['_files'] = deepcopy(files)
        new_ds.__dict__['_attributes'] = deepcopy(attrs)

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

    def __getattr__(self, name):
        if name in self.__dict__['_attributes'].keys():
            return self.__dict__['_attributes'][name](self)
        if name in self._metadata.keys():
            return self._metadata.get(name)
        raise AttributeError('%r object has no attribute %r' % (
            self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name != '__dict__':
            self.__dict__['_metadata'][name] = value

    def __repr__(self):
        return "(Dataset)"

    def __str__(self):
        return self.get_tags()

    def __iter__(self):
        """
        Iterates over all files in a dataset. Returns a tuple containing the
        path and a dictionary with the file information.
        """
        for path, info in self._files.items():
                yield (path, info)

    def __len__(self):
        return len(self._files)

    def __nonzero__(self):
        return bool(self.__dict__['_metadata'])

    def __contains__(self, item):
        """Returns True if the dataset contains the key-value pairs
        specified as kwargs.
        """
        if not isinstance(item, dict):
            return False

        if 'path' in item and item.get('path') not in self._files:
            return False

        exact = item.pop('exact', False)

        kw = item.copy()

        for k, v in kw.items():
            if k in self._metadata:
                val = self._metadata.get(k)
                if val and not utils.match(v, val, exact=exact):
                    return False
                del kw[k]

        for key in self._files:
            result = list(set([utils.match(v, self._files.get(key).get(k),
                                     exact=exact)
                               if k != 'path' else utils.match(v, key, exact=exact)
                               for k, v in kw.items()]))
            if len(result) == 1 and result[0] is True:
                break
        else:
            if kw:
                return False

        return True
