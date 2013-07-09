import sys

""" The indexfile API """

class IndexFileWrapper(object):
    __version__ = "0.9-alpha"

    path_key = 'path'
    id_key = 'labExpId'

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        if name == 'file_info':
            return [self.path_key, 'md5', 'size']
        else:
            raise AttributeError("%r object has no attribute %r" % (type(self.wrapped).__name__, name))

sys.modules[__name__] = IndexFileWrapper(sys.modules[__name__])
