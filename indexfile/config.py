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

# utility functions
def set_index_format(input_format, reset=False):
	"""Update format"""
	format_dict = input_format
	if isinstance(input_format, str):
		input_format = open(input_format, 'r')
	if isinstance(input_format, file):
		format_dict = yaml.load(input_format)
	if not hasattr(config, 'format') or reset:
		config.format = DotDict(format_dict)
	else:
		config.format.update(format_dict)

def set_config_defaults():
    """Set default values for config"""
    config.hash_algorithm = 'md5'
    config.map_only = False
    set_index_format(DEFAULT_FORMAT, True)

# initialize default config
config = DotDict()
set_config_defaults()
