"""Index module.

The module provide classes to perform operations on index files.

"""
import re
import os
import sys
import warnings
from copy import deepcopy

# default format

_format = {
    "colsep": "\t",
    "fileinfo": [
        "path",
        "size",
        "md5",
        "type",
        "view"
    ],
    "kw_sep": " ",
    "sep": "=",
    "trail": ";"
}

# utils methods

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return ' %s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line

def to_tags(kw_sep=' ', sep='=', trail=';', quote=None, **kwargs):
    taglist=[]
    #for k,v in kwargs.items():
    for k,v in dict(sorted(kwargs.items(), key=lambda k: k[0])).items():
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

# end of util methods

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
            if not v or v == '':
                v = 'NA'
            self.__setattr__(k,v)

    def add_file(self, update=False, **kwargs):
        """Add a file to the dataset files dictionary. ``kwargs`` contains
        the file information. 'path' and 'type' argument are mandatory in order
        to add the file.

        """

        path =  kwargs.get('path')
        file_type = kwargs.get('type')

        if not path:
            path = '.'

        if not file_type:
            file_type = os.path.splitext(path)[1].strip('.')

        if not self._files.get(file_type):
            self._files[file_type] = dotdict()

        if path in self._files.get(file_type).keys():
            if not update:
                warnings.warn("Entry for %s already exist..skipping." % path)
                return
            warnings.warn("Updating entry for %s." % path)

        if (not path in self._files.get(file_type).keys()) or update:
            self._files.get(file_type)[path] = dotdict()

        f = self._files.get(file_type).get(path)

        for k,v in kwargs.items():
            if not v or v == '':
                v = 'NA'
            f[k] = v

    def rm_file(self, **kwargs):
        """Remove a file form the dataset files dictionary. ``kwargs`` contains
        the file information. 'path' and 'type' argument are mandatory in order
        to add the file.

        """

        path = kwargs.get('path')
        type = kwargs.get('type')

        if not path:
            warnings.warn('[rm_file] No path found..skipping')
            return

        if not type:
            for k,v in self._files.items():
                if path in v:
                    type = k
                    break
        if type:
            del self._files.get(type)[path]
            if not self._files.get(type):
                del self._files[type]


    def export(self, types=[], tags=[]):
        """Export a :class:Dataset object to a list of dictionaries (one for each file).

        :keyword types: the list of file types to be exported. If set only the file types
                        in the list are exported. Default: [] (all types exported).

        """
        out = []
        if not tags:
            tags = self._metadata.keys() + ['type']
            if self._files:
                tags += [ k for infos in self._files.values() for info in infos.values() for k in info.keys()]
            tags = list(set(tags))
        if not types:
            types = self._files.keys()
        if not self._files:
             return [dict([(k,v) for k,v in self._metadata.items() if k in tags])]
        for type in types:
            for path,info in getattr(self,type).items():
                data = dict([(k,v) for k,v in self._metadata.items() + {'type':type}.items() + info.items() if k in tags])
                out.append(data)
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

    def __iter__(self):
        return iter([self])


class Index(object):
    """A class to access information stored into 'index files'.
    """

    def __init__(self, path=None, datasets=None, format=None):
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

        if path:
            path = os.path.abspath(path)
        self.path = path

        self.datasets = datasets or {}
        self._lock = None
        self.format = format or deepcopy(_format)
        self._lookup = {}
        self._alltags = []

    def open(self, path=None):
        """Open a file and load/import data into the index

        :param path: the path to the input file

        """
        if not path:
            path = self.path
        if type(path) == str:
            with open(os.path.abspath(path), 'r') as index_file:
                self._open_file(index_file)
            self.path = os.path.abspath(path)
        if type(path) == file:
            self._open_file(path)
            self.path = os.path.abspath(path.name)

    def set_format(self, str):
        """Set index format from json string or file

        :param str: the input string. It can be a path to a file or a valid json string.

        """

        import simplejson as json

        if not str:
            str = self._format

        try:
            format = open(str,'r')
            self.format = json.load(format)
        except:
            self.format = json.loads(str)


    def _open_file(self, index_file):
        if self.datasets:
            warnings.warn("Overwriting exisitng data")
            del self.datasets
            self.datasets = {}
        if index_file == sys.stdin:
            import tempfile
            index_file = tempfile.TemporaryFile()
            for line in sys.stdin:
                index_file.write("%s" % line)
            index_file.seek(0)
        file_type, dialect = Index.guess_type(index_file)
        index_file.seek(0)
        if dialect:
            self._load_table(index_file, dialect)
        else:
            self._load_index(index_file)


    def _load_index(self, index_file):
        """Load a file complying with the index file format.

        :param index_file: a :class:`file` object pointing to the input file

        """
        for line in index_file:
            tags = Index.parse_line(line, **self.format)

            dataset = self.insert(**tags)

    def _load_table(self, index_file, dialect=None):
        """Import entries from a SV file. The sv file must have an header line with the name of the attributes.

        :param index_file: a :class:`file` object pointing to the input file
        :keyword dialect: a :class:`csv.dialect` containg the input file format information

        """
        import csv

        reader = csv.DictReader(index_file, dialect=dialect)
        for line in reader:
            tags = Index.map_keys(line, **self.format)
            dataset = self.insert(**tags)

    def insert(self, update=False, d=None, **kwargs):
        """Add a dataset to the index. Keyword arguments contains the dataset attributes.
        """
        meta = kwargs
        if self.format.get('fileinfo'):
            meta = dict([(k,v) for k,v in kwargs.items() if k not in self.format.get('fileinfo')])
        if not d:
            d = Dataset(**meta)

        dataset = self.datasets.get(d.id)

        if dataset and update:
             warnings.warn('Updating existing dataset %s' % dataset.id)
             for k,v in meta.items():
                 if getattr(dataset, k):
                     dataset.__setattr__(k,v)

        if not dataset:
            self.datasets[d.id] = d
            dataset = self.datasets.get(d.id)
        else:
            warnings.warn('Using existing dataset %s' % dataset.id)

        if kwargs.get('path') and kwargs.get('type'):
            warnings.warn('Adding %s to dataset' % kwargs.get('path'))
            dataset.add_file(update=update, **kwargs)

        return self.datasets[d.id]

    def remove(self, **kwargs):
        """Remove dataset(s) from the index given a search query.
        """
        datasets = self.select(**kwargs).datasets.keys()
        if datasets:
            for k in datasets:
                if 'path' in kwargs:
                    self.datasets.get(k).rm_file(path=kwargs.get('path'))
                else:
                    del self.datasets['k']


    def save(self, path=None):
        """Save changes to the index file
        """
        if not path:
            path = self.path
        if path != self.path:
            self.path = os.path.abspath(path)
        with open(path,'w+') as index:
            for line in self.export(map=None):
                index.write("%s%s" % (line, os.linesep))

    def export(self, absolute=False, type='index', tags=[], header=False, **kwargs):
        """Export the index file information. ``kwargs`` contains the format information.

        :keyword absolute: specify if absolute paths should be used. Default: false
        :keyword type: specify the export type. Values: ['index','tab','json']. Default: 'index'

        """
        import simplejson as json

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

        out = []

        if type=='tab':
            if not self._alltags:
                self._create_lookup()
            headline =  self._alltags
            if tags:
                headline = tags
        for dataset in self.datasets.values():
            expd = dataset.export(tags=tags)
            for d in expd:
                line = dict()
                for k,v in d.items():
                    if k == 'id' and id:
                        k = id
                    if k == 'path' and absolute:
                        if self.path and not os.path.isabs(v):
                            v = os.path.join(os.path.dirname(self.path), os.path.normpath(v))
                    if map:
                        k = map.get(k)
                    if k:
                        line[k] = v
                if type=='index':
                    out.append(colsep.join([line.pop(path,'.'),to_tags(**dict(line.items()+kwargs.items()))]))
                if type=='json':
                    out.append(json.dumps(line))
                if type=='tab':
                    vals = line.values()
                    if tags or len(line.values()) != len(headline):
                        vals = [ line.get(l,'NA') if l != 'id' else line.get(id) for l in headline ]
                    out.append(colsep.join(vals))

        if type=='tab':
            out = list(set(out))
            if tags:
                out.sort()
            if header:
                out = [colsep.join(headline)] + out

        return out

    def _create_lookup(self):
        """Create the index lookup table for querying the index by attribute values.

        """

        if self.datasets:

            warnings.warn('Creating lookup table...')

            self._lookup = {}
            if not self.format.get('fileinfo'):
                self.format['fileinfo'] = []
            #keys = set(self.datasets.values()[0]._metadata.keys()).union(set(self.format.get('fileinfo')))
            #for k in keys:
            #    self._lookup[k] = {}
            for d in self.datasets.values():
                for k,v in d._metadata.items():
                    if k in self.format.get('fileinfo'):
                        continue
                    if k == 'id':
                        k = self.format.get('id','id')
                    if k not in self._lookup.keys():
                        self._lookup[k] = {}
                    if not self._lookup[k].get(v):
                        self._lookup[k][v] = []
                    self._lookup[k][v].append(d.id)
                for key,info in [x for x in d._files.items()]:
                    if not self._lookup.get('type'):
                        self._lookup['type'] = {}
                    if not self._lookup['type'].get(key):
                        self._lookup['type'][key] = []
                    self._lookup['type'][key].extend(info.keys())
                    for path,infos in info.items():
                        for k,v in infos.items():
                            if k in self.format.get('fileinfo'):
                                if k not in self._lookup.keys():
                                    self._lookup[k] = {}
                                if not self._lookup[k].get(v):
                                    self._lookup[k][v] = []
                                if k == 'path':
                                    self._lookup[k][v].append(path)
                                    if not self._lookup.get('_info'):
                                        self._lookup['_info'] = {}
                                    if not self._lookup['_info'].get(v):
                                        self._lookup['_info'][v] = []
                                    self._lookup['_info'][v].append(dict(set(d._metadata.items() + infos.items())))
                                else:
                                    self._lookup[k][v].append(path)

            self._alltags = [i for i in self._lookup.keys() if not i.startswith('_')]

            warnings.warn('Lookup table created successfully.')

    def select(self, id=None, oplist=['>','=','<', '!'], absolute=False, exact=False, **kwargs):
        """Select datasets from indexfile. ``kwargs`` contains the attributes to be looked for.

        :keyword id: the id to select
        :keyword absolute: specify if absolute paths should be used. Default: false

        """

        setlist = []
        finfo = {}
        meta = False

        if not id and not kwargs:
            return self

        if id:
            kwargs[self.format.get('id','id')] = id

        if kwargs:
            if set(kwargs.keys()).difference(set(self.format.get('fileinfo'))):
                meta = True
            if not self.datasets:
                if meta:
                    return self
                else:
                    return []
            if not self._lookup:
                self._create_lookup()
            for k,v in kwargs.items():
                if meta:
                    if k in self.format.get('fileinfo'):
                        finfo[k] = v
                        continue
                if not k in self._lookup.keys():
                    raise ValueError("The attribute %r is not present in the index" % k)
                if type(v) == list:
                    op = ' in '
                    val = v
                else:
                    op = "".join([x for x in list(v) if x in oplist])
                    while op in ['', '=','!']:
                        op = '%s=' % op
                    val = "".join([x for x in list(v) if x not in oplist])
                try:
                   val = int(val)
                   query = "[id for k,v in self._lookup[%r].items() if int(k)%s%r for id in v]" % (k,op,val)
                except:
                   if exact or type(val) == list:
                       search = "k%s%r" % (op,val)
                   else:
                       val = str(val)
                       search = 're.match(%r,k)' % val
                   query = "[id for k,v in self._lookup[%r].items() if %s for id in v]" % (k,search)

                setlist.append(set(eval(query)))

        if meta:
            datasets = dict([(x,self.datasets.get(x)) for x in set.intersection(*setlist) if self.datasets.get(x)])
            i = Index(datasets=datasets, format=self.format, path=self.path)
            i._create_lookup()
        else:
            filelist = [x for x in set.intersection(*setlist) if "/" in x]
            if absolute:
                filelist = [os.path.join(os.path.dirname(self.path),x) if not os.path.isabs(x) and self.path else x for x in filelist]
            i = Index(format=self.format, path=self.path)
            for f in filelist:
                for info in self._lookup['_info'].get(f):
                    i.insert(**info)
            i._create_lookup()

        if finfo and meta:
            i = i.select(None,oplist,absolute,exact,**finfo)

        return i

    @property
    def size(self):
        return len(self.datasets)

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
        columns = file.readline().split("\t")
        if len(columns) == 2 and ';' in columns[1]:
            return "idx", None

        import csv

        if not csv.Sniffer().has_header(file.readline()):
            raise ValueError('Metadata file must have a header')
        file.seek(0)

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
        expr = '(?P<key>[^ ]+)%s\"?(?P<value>[^%s\"]*)\"?%s' % (sep, trail, trail)
        for match in re.finditer(expr, tags):
            key = match.group('key')
            if key == id:
                key = 'id'
            tagsd[key] = match.group('value')

        if not tagsd:
            if os.path.isfile(os.path.abspath(tags)):
                file = os.path.abspath(tags)

        tagsd['path'] = file

        return tagsd

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

        out = {}
        if map:
            for k,v in map.items():
                if not v:
                    map.pop(k)
                    continue
                map[v] = k

        for k,v in obj.items():
            key = k
            if map:
                key = map.get(k)
            if key:
                if key == id:
                    key = "id"
                out[key] = v
        return out


