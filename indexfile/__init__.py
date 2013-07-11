import sys
from .index import *

class IndexFileWrapper(object):
    """ The indexfile API """

    __version__ = "0.9-alpha"

    path_key = 'path'
    id_key = 'labExpId'
    _file_info = ['type', 'view', 'md5', 'size']
    _meta_info = []

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        if name == 'file_info':
            return self._file_info + [self.path_key]
        else:
            raise AttributeError("%r object has no attribute %r" % (type(self.wrapped).__name__, name))

sys.modules[__name__] = IndexFileWrapper(sys.modules[__name__])
