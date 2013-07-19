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

    def __init__(self, **kwargs):
        """Create an instance of the Dataset class

        Arguments:
        ----------
         -  a dictionary containing the metadata information
        """
        import indexfile

        self.__dict__['_metadata'] = {}
        self.__dict__['_files'] = dotdict()
        self.__dict__['_attributes'] = {}

        self.__dict__['_tag_id'] = indexfile._id_key
        self.__dict__['_tag_path'] = indexfile._path_key
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

    def export(self, absolute=False, types=[]):
        """Convert an index entry object to its string representation in index file format
        """
        out = []
        if not types:
            types = self._files.keys()
        for type in types:
            try:
                for path,info in getattr(self,type).items():
                    if absolute:
                        path = os.path.abspath(path)
                    tags = ' '.join([self.get_tags(),to_tags(**info)])
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

    def folder(self, name=None):
        """Resolve a folder based on datasets project folder and
        if type_folders. If type folders is True, this always resolves
        to the data folder. Otherwise, if name is specified, it resolves
        to the named folder under this datasets data folder.
        """
        if not self.type_folders or name is None:
            return self.data_folder
        else:
            return os.path.join(self.data_folder, name)

    def get_genome(self, config):
        """Return the default index that should be used by this dataset
        """
        try:
            sex = self.sex.lower()
            if not config.get('.'.join(['genomes', sex, 'path'])):
                sex = { 'm': 'male',
                        'f': 'female'
                        }.get(sex, None)
            return config.get('.'.join(['genomes', sex, 'path']))
        except:
            return None

    def get_index(self, config):
        """Return the default index that should be used by this dataset
        """
        return config.get('.'.join(['genomes', self.sex, 'index']))

    def get_annotation(self, config):
        """Return the default annotation that should be used for this
        dataset
        """
        try:
            sex = self.sex
            return config.get('.'.join(['annotations', self.sex, 'path']))
        except:
            return None

    def _get_fastq(self, sort_by_name=True):
        self.type_folders = False
        self.data_folder = os.path.dirname(self.primary)
        if os.path.split(self.data_folder)[1] == "fastq":
            self.type_folders = True
            self.data_folder = os.path.split(self.data_folder)[0]

        directory = os.path.dirname(self.primary)
        if sort_by_name and len(self.fastq) > 1:
            s = sorted([self.fastq[0], self.fastq[1]], key = lambda x: x.path)
            self.fastq[0] = s[0]
            self.fastq[1] = s[1]

    def __getattr__(self, name):
        if name == 'id':
            return self._metadata.get(self._tag_id)
        if name == 'file_info':
            return [self._tag_path] + self._file_info
        if name == 'meta_info':
            return [self._tag_id] + self._meta_info
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
                name = self._tag_id
            if name == 'path':
                name = self._tag_path
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

    @staticmethod
    def find(path):
        """Find dataset from path. Detect if paired and find mate
        file if possible

        path: path to the input file

        return:
            None if no dataset found
            [name, mate1] if single end
            [name, mate1, mate2] if paired end
        """

        basedir = os.path.dirname(path)
        name = os.path.basename(path)
        expr_paired = "^(?P<name>.*)(?P<delim>[_\.-])" \
               "(?P<id>\d)\.(?P<type>fastq|fq)(?P<compression>\.gz)*?$"
        expr_single = "^(?P<name>.*)\.(fastq|fq)(\.gz)*?$"
        match = re.match(expr_paired, name)
        if match:
            try:
                id = int(match.group('id'))
                if id < 2:
                    id += 1
                else:
                    id -= 1
                compr = match.group("compression")
                if compr is None:
                    compr = ""
                files = [path, os.path.join(basedir, "%s%s%d.%s%s")
                                                    % (match.group('name'),
                                                    match.group('delim'),
                                                    id, match.group('type'),
                                                    compr)]
                files.sort()

                return match.group('name'), files
            except:
                pass
        match = re.match(expr_single, name)
        if match:
            return match.group('name'), [path]
        return None

    @staticmethod
    def find_secondary(name):
        """Find secondary dataset file and return the basename of
        that file or return None
        """

        basedir = os.path.dirname(name)
        name = os.path.basename(name)
        expr = "^(?P<name>.*)(?P<delim>[_\.-])" \
               "(?P<id>\d)\.(?P<type>fastq|fq)(?P<compression>\.gz)*?$"
        match = re.match(expr, name)
        if match is not None:
            try:
                id = int(match.group("id"))
                if id < 2:
                    id += 1
                else:
                    id -= 1
                compr = match.group("compression")
                if compr is None:
                    compr = ""
                return match.group("name"), os.path.join(basedir, "%s%s%d.%s%s"
                                        % (match.group("name"),
                                           match.group("delim"),
                                           id, match.group("type"),
                                           compr))
            except Exception:
                pass
        return None


class IndexDefinition(object):
    """A class to specify the index meta information
    """

    data = {}

##### TODO: not hardcode this information ##############################
    data['id'] = 'labExpId'
    data['metainfo'] = ['labProtocolId',
                'dataType',
                'age',
                'localization',
                'sraStudyAccession',
                'lab',
                'sex',
                'cell',
                'rnaExtract',
                'tissue',
                'sraSampleAccession',
                'readType',
                'donorId',
                'ethnicity'
                ]
    data['fileinfo'] = ['type',
                'size',
                'md5',
                'view'
                ]

    data['file_types'] = ['fastq', 'bam', 'bai', 'gff', 'map', 'bigWig', 'bed']

    #data['default_path'] = '.index'
######################################################################

    @classmethod
    def dump(cls, tabs=2):
        return json.dumps(cls.data, indent=tabs)

class IndexFile(object):
    """A class to access information stored into 'index files'.
    """

    def __init__(self, path=".index", datasets={}, clear=False):
        """Creates an instance of an IndexFile class

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

