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



# setup logger
import indexfile
# Disable warning about invalid constant name
# pylint: disable=C0103
log = indexfile.getLogger(__name__)
# pylint: enable=C0103

class Dataset(dict):
    """A class that represent dataset in the index file.

    Each entry is identified by a dataset id (eg. labExpId) and has metadata
    information as long as file information.
    """

    def __init__(self, fileinfo=None, **kwargs):
        """Create an instance of a Dataset. ``kwargs`` contains
        the dataset attributes.

        """
        self.__dict__['_metadata'] = DotDict()
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
            log.debug('No path specified. Skipping')
            return

        if not file_type:
            log.debug('Get file type from file extension')
            file_type = os.path.splitext(path)[1].strip('.')
            kwargs['type'] = file_type

        if path in self._files and not update:
            log.debug("Skip existing %s entry", path)
            return

        if not path in self._files:
            self._files[path] = {}

        for key, val in kwargs.items():
            if key == 'path' or key not in fileinfo:
                continue
            if not val or val == '':
                log.debug('Replace missing value with NA for %s', key)
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
            for f in [v for k,v in self._files.items()
                      if v.type == type]:
                del f


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
                data = dict([(k, v) for k, v in self._metadata.items()
                            + {'path': path, 'type': info.type}.items()
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


    def get(self, *args, **kwargs):
        """Return a clone of the dataset if it contains the key-value pairs
        specified in kwargs
        """

        if args and len(args) == 1:
            return self._files.get(args[0])
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
                        if match(v, value.get(k), exact=exact)]
            if not path:
                return None
            files.append(set(path))
        if not files:
            return None
        return self.clone(list(set.intersection(*files)))


    def clone(self, paths=None):
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


    def __getitem__(self, key):
        return self._files.get(key)


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
        return "(Dataset %s)" % (self.id)

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
                if val and not match(str(v), str(val), exact=exact):
                    return False
                del kw[k]

        for key in self._files:
            result = list(set([match(v, self._files.get(key).get(k),
                                     exact=exact)
                               if k != 'path' else match(v, key, exact=exact)
                               for k, v in kw.items()]))
            if len(result) == 1 and result[0] is True:
                break
        else:
            if kw:
                return False

        return True
