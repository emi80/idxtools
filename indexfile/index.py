"""Index module providing functionality around indexfile format
"""
import re
import os
import json
import sys

def to_tags(tag_sep=' ', kw_sep='=', kw_trail=';', **kwargs):
    taglist=[]
    for k,v in kwargs.items():
        v = str(v)
        if v.find(' ') > 0:
            v= '\"%s\"' % v
        taglist.append('%s%s%s%s' % (k, kw_sep, v, kw_trail))
    return tag_sep.join(taglist)

class dotdict(dict):
    def __init__(self, d={}):
        for k,v in d.items():
            if hasattr(v, 'keys'):
                v = dotdict(v)
            self[k] = v

    def __getattr__(self, name):
        return self.get(name)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Dataset(object):
    """A class that represent dataset entry in the index file.

    Each entry is identified by the dataset name (eg. labExpId) and has metadata
    information as long as file information in order to be able to retrieve files
    and information related to the sample.
    """

    def __init__(self, format={}, **kwargs):
        """Create an instance of the Dataset class

        Arguments:
        ----------
         -  a dictionary containing the metadata information
        """
        import indexfile

        self.__dict__['_metadata'] = {}
        self.__dict__['_files'] = dotdict()
        self.__dict__['_attributes'] = {}

        self.__dict__['_format'] = indexfile._format
        self.__dict__['_meta_info'] = indexfile._meta_info
        self.__dict__['_file_info'] = indexfile._file_info


        for k,v in kwargs.items():
            self.__setattr__(k,v)

    def add_file(self, path, file_type, absolute=False, **kwargs):
        """Add the path of a file related to the dataset to the class files dictionary

        path - the path of the file
        file_type - the type of the file
        """

        if absolute:
            path = os.path.abspath(path)

        if not self._files.get(file_type):
            self._files[file_type] = dotdict()

        if not path in self._files.get(file_type).keys():
            self._files.get(file_type)[path] = dotdict()

        f = self._files.get(file_type).get(path)

        for k,v in kwargs.items():
            f[k] = v

    def export(self, absolute=False, types=[], jsonout=False):
        """Convert an index entry object to its string representation in index file format
        """
        out = []
        if not types:
            types = self._files.keys()
        for type in types:
            try:
                for path,info in getattr(self,type).items():
                    if jsonout:
                        out.append(json.dumps(dict(self._metadata.items() + {'path':path, 'type':type}.items() + info.items())))
                    else:
                        if absolute:
                            path = os.path.abspath(path)
                        tags = ' '.join([self.get_tags(),to_tags(**{'type':type}),to_tags(**info)])
                        out.append('\t'.join([path, tags]))
            except:
                pass
        return out

    def get_tags(self, tags=[], exclude=[]):
        """Concatenate specified tags using the provided tag separator. The tag are formatted
        according to the 'index file' format

        Keyword arguments:
        -----------
        tags - list of keys to be included into output. Default value is
               the empty list, which means that all tags will be returned.
        exclude  - list of keys to be excluded from output. Default value is
                    the empty list meaning that all keys will be included.
        """
        if not tags:
            tags = self._metadata.keys()
        tags = list(set(tags).difference(set(exclude)))
        data = dict(filter(lambda i:i[0] in tags, self._metadata.iteritems()))
        return to_tags(**data)

    def __getattr__(self, name):
        if name == 'id':
            return self._metadata.get(self._format.get('id'))
        if name == 'file_info':
            return [self._format.get('path')] + self._file_info
        if name == 'meta_info':
            return [self._format.get('id')] + self._meta_info
        if name in self.__dict__['_attributes'].keys():
            return self.__dict__['_attributes'][name](self)
        if name in self._metadata.keys():
            return self._metadata.get(name)
        if name in self._files.keys():
            return self._files.get(name)
        raise AttributeError('%r object has no attribute %r' % (self.__class__.__name__,name))

    def __setattr__(self, name, value):
        import indexfile
        if name != '__dict__':
            if name == 'id':
                name = self._format.get('id')
            if name == 'path':
                name = self._format.get('path')
            if name in self.file_info:
                raise ValueError("File information %r detected. To add this please add a file to the dataset." % name)
            if not indexfile._meta_info or name in indexfile._meta_info:
                self.__dict__['_metadata'][name] = value
                return
            raise ValueError("Cannot add %r information" % name)

    def __repr__(self):
        return "Dataset: %s" % (self.id)

    def __str__(self):
        return self.get_tags()


class Index(object):
    """A class to access information stored into 'index files'.
    """

    def __init__(self, path=None, datasets={}, clear=False):
        """Creates an instance of an Index

        path - path of the index file

        Keyword arguments:
        datasets -  a list containing all the entries as dictionaries. Default empty list.
        """

        self.path = path
        self.datasets = datasets
        self._lock = None

        if not self.datasets:
            indices = path
            if not isinstance(indices, list):
                indices = [indices]
            for index in indices:
                if os.path.exists(index):
                    self.load(index, clear)

    def load(self, path, clear=False):
        """Add datasets to the index object by parsing an index file

        path -- path of the index file

        Keyword arguments:
        clear -- specify if index clean up is required before loadng (default False)
        """
        if clear:
            self.datasets = {}
        with open(os.path.abspath(path), 'r') as index_file:
            for line in index_file:
                self._parse_line(line)

    def save(self):
        """Save changes to the index file
        """
        with open(self.path,'w+') as index:
           self.export(out=index)


    def _parse_line(self, line):
        """Parse a line of the index file and append the parsed entry to the entries list.

        line - the line to be parsed
        """
        expr = '^(?P<file>.+)\t(?P<tags>.+)$'
        match = re.match(expr, line)
        file = match.group('file')
        tags = match.group('tags')

        meta = Metadata.parse(tags)
        dataset = self.datasets.get(meta.labExpId, None)

        if not dataset:
            dataset = Dataset(meta)
            self.datasets[dataset.id] = dataset

        dataset.add_file(file, meta)

    @classmethod
    def parse(cls, string, info=[]):
        """Parse a string of concatenated tags and converts it to a Metadata object

        Arguments:
        ----------
        string - the concatenated tags
        """
        tags = cls._parse_tags(string)
        return Metadata(tags)

    @classmethod
    def _parse_tags(cls, str, sep='=', trail=';'):
        """Parse key/value pair tags from a string and returns a dictionary

        Arguments:
        ----------
        str - the tags string

        Keyword arguments:
        ------------------
        sep   -  the separator between key and value of the tag. Default is '='.
        trail -  trailing character of the tag. Default ';'.
        """
        tags = {}
        expr = '(?P<key>[^ ]+)%s(?P<value>[^%s]*)%s' % (sep, trail, trail)
        for match in re.finditer(expr, str):
            tags[match.group('key')] = match.group('value')
        return tags


    def add_dataset(self, metadata, id=None):
        if not id:
            id = length(self.datasets)
        dataset = self.datasets.get(id, None)
        if dataset:
            raise ValueError("Dataset %r already exists" % id)
        self.datasets[id] = Dataset(metadata)
        return self.datasets[id]

    def export(self, out=None, absolute=False):
        """Save changes made to the index structure loaded in memory to the index file
        """
        if not out:
            out = sys.stdout
        for dataset in self.datasets.values():
            for line in dataset.export(absolute=absolute):
                out.write('%s%s' % (line, os.linesep))


    def lock(self):
        """Lock the index"""
        if self._lock is not None:
            return False

        from lockfile import LockFile

        base = os.path.dirname(self.path)
        if not os.path.exists(base):
            os.makedirs(base)

        self._lock = LockFile(self.path)
        try:
            self._lock.acquire()
            return True
        except Exception, e:
            raise StoreException("Locking index file failed: %s" % str(e))

    def release(self):
        if self._lock is None:
            return False
        self._lock.release()
        self._lock = None
        return True

class _OnSuccessListener(object):
    def __init__(self, project, config):
        self.project = project
        self.config = config
    def __call__(self, tool, args):
        # grape.grape has an import grape.index.* so we
        # import implicitly here to avoid circular dependencies
        from .grape import Project

        project = Project(self.project)
        index = project.index
        try:
            index.lock()
            for k in tool.__dict__['outputs']:
                v = self.config[k]
                if os.path.exists(v):
                    name, ext = os.path.splitext(v)
                    if ext == '.gz':
                        name, ext = os.path.splitext(name)
                    info = {'type': ext.lstrip('.'), 'md5': utils.md5sum(v)}
                    if self.config.has_key('view') and self.config['view'].get(k, None):
                        info['view'] = self.config['view'][k]
                    index.add(self.config['name'], v, info)
            index.save()
        finally:
            index.release()

def prepare_tool(tool, project, config):
    """Add listeners to the tool to ensure that it updates the index
    during execution.

    :param tool: the tool instance
    :type tool: jip.tools.Tool
    :param project: the project
    :type project: grape.Project
    :param name: the run name used to identify the job store
    :type name: string
    """
    tool.on_success.append(_OnSuccessListener(project, config))

