"""
Indexfile main configuration
"""
import yaml
from .utils import DotDict

# default index format
DEFAULT_FORMAT = {
    "colsep": "\t",
    "fileinfo": set((
        "path",
        "size",
        "type",
        "view"
    )),
    "kw_sep": " ",
    "rep_sep": ",",
    "sep": "=",
    "trail": ";"
}

# output formats
OUTPUT_FORMATS = {
    'index': DEFAULT_FORMAT.copy(),
    'tsv': {
        'colsep': '\t',
    },
    'csv': {
        'colsep': ','
    },
    'json': {},
    'yaml': {}
}


def set_config_defaults():
    """Set default values for config"""
    config.hash_algorithm = 'md5'
    config.map_only = False
    config.loglevel = indexfile._log_level
    config.format = DEFAULT_FORMAT

class Config(DotDict):
    """Config class that extends DotDict"""

    def update(self, other=None, **kwargs):
        """Update a DotDict supporting nested attribute access"""
        if 'format' in kwargs:
            kwargs['format'] = Config._get_dict(kwargs['format'])
        # call update from superclass
        super(Config, self).update(other, **kwargs)

    def __setitem__(self, key, value):
        if key == 'format':
           value = Config._get_dict(value) 
        DotDict.__setitem__(self, key, value)

    @staticmethod
    def _get_dict(fp):
        if isinstance(fp, str):
            fp = open(fp, 'r')
        if isinstance(fp, file):
            fp = yaml.load(fp)
        return fp

    __setattr__ = __setitem__


# initialize default config
config = Config()
set_config_defaults()
