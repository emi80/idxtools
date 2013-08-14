"""Index module.

The module provide classes to perform operations on index files.

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
    """A class that represent dataset in the index file.

    Each entry is identified by a dataset id (eg. labExpId) and has metadata
    information as long as file information.
    """

    def __init__(self, **kwargs):
        """Create an instance of a Dataset. ``kwargs`` contains
        the dataset attributes.

        """
        self.__dict__['_metadata'] = {}
        self.__dict__['_files'] = dotdict()
        self.__dict__['_attributes'] = {}

        for k,v in kwargs.items():
            self.__setattr__(k,v)

    def add_file(self, absolute=False, **kwargs):
        """Add a file to the dataset files dictionary. ``kwargs`` contains
        the file information. 'path' and 'type' argument are mandatory in order
        to add the file.

        :keyword absolute: specifies if an absolute path should be used. Default: False
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
        """Export a :class:Dataset object to a list of dictionaries (one for each file).

        :keyword absolute: specify if an absolute path should be used. Deafult: False
        :keyword types: the list of file types to be exported. If set only the file types
                        in the list are exported. Defalut: [] (all types exported).

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
        """Concatenate specified tags. The tag are formatted according to the index file format

        :keyword tags: list of keys to be included into output. Default: [] (all tags returned).
        :keyword exclude: list of keys to be excluded from output. Default: [] (all keys included).

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

    def __init__(self, path=None, datasets={}, format={}):
        """Creates an instance of an Index

        :param path: the path to the index file
        :keyword datasets: a list containing all the entries as dictionaries. Default: [].
        :keyword format: a dictionary containing the format and mapping information. Default: {}.

        The format information can be expressed with a dictionary as follows:

        :key fileinfo: a list with the names of the keys related to files
        :key id: the dataset identifier name. Default: 'id'
        :key map: a dictionary contatining the mapping information
        :key sep: the key/value separator character
        :key trail: the key/value pair trailing character
        :key kw_sep: the keywords separator character

        """

        self.path = path

        self.datasets = datasets
        self._lock = None
        self.format = format
        self._lookup = {}

        if self.path:
            self.initialize()

    def initialize(self):
        """Initialize the index with data

        """
        if not self.path:
            raise ValueError("No index to load. Please specify a path")
        if self.datasets:
            warnings.warn("The index already contains data. Merging with data from file.")

        self.load(self.path)

    def open(self, path):
        """Open a file and load/import data into the index

        :param path: the path to the input file

        """
        with open(os.path.abspath(path), 'r') as index_file:
            if self.datasets:
                warnings.warn("Overwrting exisitng data")
                del self.datasets
                self.datasets = {}
            file_type, dialect = Index.guess_type(index_file)
            index_file.seek(0)
            if dialect:
                self.load_table(index_file, dialect)
            else:
                self.load_index(index_file)
            self.path = path

    def load_index(self, index_file):
        """Load a file complying with the index file format.

        :param index_file: a :class:`file` object pointing to the input file

        """
        for line in index_file:
            file,tags = Index.parse_line(line, **self.format)

            dataset = self.insert(**tags)
            dataset.add_file(path=file, **tags)

    def load_table(self, index_file, dialect=None):
        """Import entries from a SV file. The sv file must have an header line with the name of the attributes.

        :param index_file: a :class:`file` object pointing to the input file
        :keyword dialect: a :class:`csv.dialect` containg the input file format information

        """
        import csv

        reader = csv.DictReader(index_file, dialect=dialect)
        for line in reader:
            tags = Index.map_keys(line, **self.format)
            dataset = self.insert(**tags)
            dataset.add_file(**tags)

    def insert(self, **kwargs):
        """Add a dataset to the index. Keyword arguments contains the dataset attributes.
        """
        d = Dataset(**kwargs)
        dataset = self.datasets.get(d.id)

        if not dataset:
            self.datasets[d.id] = d
            dataset = self.datasets.get(d.id)
        else:
            warnings.warn('Using existing dataset %s' % dataset.id)

        if kwargs.get('path') and kwargs.get('type'):
            warnings.warn('Adding %s to dataset' % kwargs.get('path'))
            dataset.add_file(**kwargs)

        return self.datasets[d.id]

    def save(self):
        """Save changes to the index file
        """
        with open(self.path,'w+') as index:
            for line in self.export():
                index.write("%s%s" % (line, os.linesep))

    def export(self, absolute=False, type='index', **kwargs):
        """Export the index file information. ``kwargs`` contains the format information.

        :keyword absolute: specify if absolute paths should be used. Default: false
        :keyword type: specify the export type. Values: ['index','tab','json']. Default: 'index'

        """
        import json

        if self.format:
            if not kwargs:
                kwargs = {}
            kwargs = dict(self.format.items() + kwargs.items())

        id = kwargs.pop('id',None)
        map = kwargs.pop('map',None)
        colsep = kwargs.pop('colsep','\t')
        fileinfo = kwargs.pop('fileinfo',[])
        if map:
            for k,v in map.items():
                if v: map[v] = k
        else:
            map = {}

        path = map.get('path','path')

        if type=='tab':
            header = []

        out = []
        for dataset in self.datasets.values():
            expd = dataset.export(absolute=absolute)
            for d in expd:
                line = dict()
                for k,v in d.items():
                    if k == 'id':
                        if id: k = id
                    if map:
                        k = map.get(k)
                    if k:
                        line[k] = v
                if type=='index':
                    out.append(colsep.join([line.pop(path,'.'),to_tags(**dict(line.items()+kwargs.items()))]))
                if type=='json':
                    out.append(json.dumps(line))
                if type=='tab':
                    if not header:
                        header = line.keys()
                        out.append(colsep.join(header))
                    if len(line.values()) != len(header):
                        raise ValueError('Found lines with different number of fields. Please check your input file.')
                    out.append(colsep.join(line.values()))
        return out

    def _create_lookup(self):
        """Create the index lookup table for querying the index by attribute values.

        """
        if self.datasets:
            warnings.warn('Creating lookup table...')
            self._lookup = {}
            for k in self.datasets.values()[0]._metadata.keys():
                self._lookup[k] = {}
            for d in self.datasets.values():
                for k,v in d._metadata.items():
                    if not self._lookup[k].get(v):
                        self._lookup[k][v] = []
                    self._lookup[k][v].append(d.id)
            warnings.warn('Lookup table created successfully.')

    def select(self, id=None, oplist =  ['>','=','<', '!'], **kwargs):
        """Select datasets from indexfile. ``kwargs`` contains the attributes to be looked for.

        :keyword id: the id to select

        """

        setlist = []

        if id:
            setlist.append(set(list(self.datasets.get(id,[]))))

        if kwargs:
            if not self._lookup:
                self._create_lookup()
            for k,v in kwargs.items():
                #if k in format.get('file_info'):
                #    finfo.append(k)
                #    continue
                if not k in self._lookup.keys():
                    raise ValueError("The attribute %r is not present in the index" % k)
                op = "".join([x for x in list(v) if x in oplist])
                while op in ['', '=','!']:
                    op = '%s=' % op
                val = "".join([x for x in list(v) if x not in oplist])
                try:
                    val = int(val)
                    query = "[id for k,v in self._lookup[%r].items() if int(k)%s%r for id in v]" % (k,op,val)
                except:
                    query = "[id for k,v in self._lookup[%r].items() if k%s%r for id in v]" % (k,op,val)
                setlist.append(set(eval(query)))

        datasets = dict([(x,self.datasets.get(x)) for x in set.intersection(*setlist)])

        i = Index(datasets=datasets)
        i._create_lookup()

        return i

    def lock(self):
        """Lock this index file

        """
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
        """Release a lock on this index file

        """
        if self._lock is None:
            return False
        self._lock.release()
        self._lock = None
        return True

    @classmethod
    def guess_type(cls, file, trail=';', delimiters=None):
        """Guess type of an input file for importing data into the index.

        :param file: the input file
        :keyword trail: the trailing charachter of each key/value pair
        :keyword delimiters: the allowed fields delimiters

        """
        import csv

        if not csv.Sniffer().has_header(file.readline()):
            raise ValueError('Metadata file must have a header')

        dialect = csv.Sniffer().sniff(file.readline(), delimiters=delimiters)
        file.seek(0)

        if dialect.delimiter == ',':
            return 'csv', dialect

        reader = csv.DictReader(file, dialect=dialect)

        if len(reader.fieldnames)<2:
            raise ValueError('Not enough columns in metadata file')

        if trail in reader.fieldnames[1]:
            return 'index', None

        return 'tsv', dialect

    @classmethod
    def parse_line(cls, str, **kwargs):
        """Parse an index file line and returns a tuple with
        the path to the file referred by the line (if any) and a
        dictionary with the parsed key/value pairs. ``kwargs`` is
        used to specify the index format information.

        :param str: the line to parse

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

    @classmethod
    def map_keys(cls, obj, **kwargs):
        """ Maps ``obj`` keys using the mapping information contained
        in the arguments. ``kwargs`` is used to specify the index format
        information.

        :param obj: the input dictionary

        """
        if not obj:
            return {}

        id = kwargs.get('id')
        map = kwargs.get('map',{})

        if not map:
            return obj

        for k,v in map.items():
            if not v:
                map.pop(k)
                continue
            map[v] = k

        out = {}
        for k,v in obj.items():
            key = map.get(k)
            if key:
                if key == id:
                    key = "id"
                out[key] = v
        return out


