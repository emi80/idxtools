"""Index module providing functionality around indexfile format
"""
import re
import os
import json
import sys
import warnings

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return ' %s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line

def to_tags(kw_sep=' ', sep='=', trail=';', quote=None, **kwargs):
    taglist=[]
    for k,v in kwargs.items():
        v = str(v)
        if quote:
            if quote=='value' or quote=='both':
                if '\"' not in v: v = '\"%s\"' % v
            if quote=='key' or quote=='both':
                if '\"' not in k: k = '\"%s\"' % k
        if ' ' in v:
            if '\"' not in v: v = '\"%s\"' % v
        taglist.append('%s%s%s%s' % (k, sep, v, trail))
    return kw_sep.join(taglist)

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

    def __init__(self, **kwargs):
        """Create an instance of the Dataset class

        Arguments:
        ----------
         -  a dictionary containing the metadata information
        """
        self.__dict__['_metadata'] = {}
        self.__dict__['_files'] = dotdict()
        self.__dict__['_attributes'] = {}

        for k,v in kwargs.items():
            self.__setattr__(k,v)

    def add_file(self, absolute=False, **kwargs):
        """Add the path of a file related to the dataset to the class files dictionary

        path - the path of the file
        file_type - the type of the file
        """

        if not kwargs.get('path'):
            raise ValueError("Please specify a path for the file")

        if not kwargs.get('type'):
            raise ValueError("Please specify a type for the file")

        path =  kwargs.get('path')
        file_type = kwargs.get('type')

        if absolute:
            path = os.path.abspath(path)

        if not self._files.get(file_type):
            self._files[file_type] = dotdict()

        if path in self._files.get(file_type).keys():
            warnings.warn("Entry for %s already exist..skipping." % path)
            return

        if not path in self._files.get(file_type).keys():
            self._files.get(file_type)[path] = dotdict()

        f = self._files.get(file_type).get(path)

        for k,v in kwargs.items():
            f[k] = v

    def export(self, absolute=False, types=[]):
        """Convert an index entry object to its string representation in index file format. Optionally the output format can be json.
        """
        out = []
        if not types:
            types = self._files.keys()
        for type in types:
            for path,info in getattr(self,type).items():
                if absolute:
                    path = os.path.abspath(path)
                tags = dict(self._metadata.items() + {'type':type}.items() + info.items())
                out.append(tags)
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
        data = dict([i for i in self._metadata.iteritems() if i[0] in tags])
        return to_tags(**data)

    def __getattr__(self, name):
        if name in self.__dict__['_attributes'].keys():
            return self.__dict__['_attributes'][name](self)
        if name in self._metadata.keys():
            return self._metadata.get(name)
        if name in self._files.keys():
            return self._files.get(name)
        raise AttributeError('%r object has no attribute %r' % (self.__class__.__name__,name))

    def __setattr__(self, name, value):
        if name != '__dict__':
            self.__dict__['_metadata'][name] = value

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
        self.format = { 'id':'labExpId' }

        self.initialize(clear)

    def initialize(self, clear=False):
        """Initialize the index with data

        """
        if not self.path:
            raise ValueError("No index to load. Please specify a path")
        if self.datasets:
            warnings.warn("The index already contains data. Merging with data from file.")

        self.load(self.path, clear)

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
                file,tags = Index.parse(line, **self.format)

                dataset = self.add_dataset(**tags)
                dataset.add_file(path=file, **tags)

    def add_dataset(self, **kwargs):
        #meta = set(kwargs.keys()).difference(format.file_info+['path'])
        #d = Dataset(**{k: kwargs.get(k) for k in meta})
        d = Dataset(**kwargs)
        dataset = self.datasets.get(d.id)

        if not dataset:
            self.datasets[d.id] = d
        else:
            warnings.warn('Using existing dataset %s' % dataset.id)

        if kwargs.get('path') and kwargs.get('type'):
            warnings.warn('Adding %s to existing dataset' % kwargs.get('path'))
            dataset.add_file(**kwargs)

        return self.datasets[d.id]

    def save(self):
        """Save changes to the index file
        """
        with open(self.path,'w+') as index:
            for line in self.export():
                index.write("%s%s" % (line, os.linesep))

    def export(self, absolute=False, json=False, **kwargs):
        """Save changes made to the index structure loaded in memory to the index file
        """
        import json as j

        id = kwargs.get('id')
        colsep = kwargs.get('colsep','\t')

        out = []
        for dataset in self.datasets.values():
            d = dataset.export(absolute=absolute)
            for line in d:
                for k,v in line.items():
                    if id and k == 'id':
                        line[id] = v
                        del line['id']
                if json:
                    out.append(j.dumps())
                else:
                    out.append(colsep.join([line.get('path'),to_tags(**line)]))
        return out

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

    @classmethod
    def parse(cls, str, **kwargs):
        """Parse key/value pair tags from a string and returns a dictionary

        Arguments:
        ----------
        str - the string to parse.

        Keyword arguments:
        ------------------
        sep   -  the separator between key and value of the tag. Default is '='.
        trail -  trailing character of the tag. Default ';'.
        """
        file = None
        tags = str

        sep = kwargs.get('sep','=')
        trail = kwargs.get('trail',';')
        id = kwargs.get('id')

        expr = '^(?P<file>.+)\t(?P<tags>.+)$'
        match = re.match(expr, str)
        if match:
            file = match.group('file')
            tags = match.group('tags')

        tagsd = {}
        expr = '(?P<key>[^ ]+)%s(?P<value>[^%s]*)%s' % (sep, trail, trail)
        for match in re.finditer(expr, tags):
            key = match.group('key')
            if key == id:
                key = 'id'
            tagsd[key] = match.group('value')

        if not tagsd:
            if os.path.isfile(os.path.abspath(tags)):
                file = os.path.abspath(tags)

        return file,tagsd


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

