"""
Indexfile main configuration
"""
import os
import yaml
import locale
import logger
from .utils import DotDict

# default config attributes
DEFAULT_HASH_ALGORITHM = 'md5'
DEFAULT_OUTPUT_FORMAT = 'index'
DEFAULT_MISSING_VALUE = 'NA'

# default descriptors for Dataset
DEFAULT_ID_DESCRIPTOR = 'id'
DEFAULT_PATH_DESCRIPTOR = 'path'
DEFAULT_TYPE_DESCRIPTOR = 'type'
DEFAULT_FILEINFO = [ DEFAULT_PATH_DESCRIPTOR, DEFAULT_TYPE_DESCRIPTOR, DEFAULT_HASH_ALGORITHM ]

# output formats
OUTPUT_FORMATS = {
    'index': {
        "col_sep": "\t",
        "tag_sep": " ",
        "rep_sep": ",",
        "kw_sep": "=",
        "kw_trail": ";"
    },
    'tsv': {
        'col_sep': '\t',
    },
    'csv': {
        'col_sep': ','
    },
    'json': {},
    'yaml': {}
}

# merge types
class MergeTypes:
    First, All, Sum, Check = range(4)


def _get_dict(fp):
    if isinstance(fp, str):
        fp = open(fp, 'r')
    if isinstance(fp, file):
        fp = yaml.load(fp)
    return fp


class Config(DotDict):
    """Config class extending DotDict"""

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.reset()

    def update(self, other=None, **kwargs):
        """Update a Config object"""
        other = _get_dict(other)
        # call update from superclass
        super(Config, self).update(other, **kwargs)

    def reset(self):
        """Set default values for config"""
        self.hash_algorithm = DEFAULT_HASH_ALGORITHM
        self.map_only = False
        self.loglevel = logger._log_level
        self.format = DotDict(OUTPUT_FORMATS[DEFAULT_OUTPUT_FORMAT])
        self.id_desc = DEFAULT_ID_DESCRIPTOR
        self.path_desc = DEFAULT_PATH_DESCRIPTOR
        self.type_desc = DEFAULT_TYPE_DESCRIPTOR
        self.fileinfo = DEFAULT_FILEINFO[:]
        self.missing_value = DEFAULT_MISSING_VALUE
        self.map = DotDict()
        self.merge_type = MergeTypes.All
        self.decimal_point = locale.localeconv()['decimal_point']

    def load(self, fp):
        """Load configuration from file or dir"""
        if not fp:
            return
        self.update(_get_dict(fp))


# initialize default config
config = Config()
