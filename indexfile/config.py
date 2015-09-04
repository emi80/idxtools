"""
Indexfile main configuration
"""
import yaml
from .utils import DotDict

# initialize default config
config = DotDict()
config.fileinfo = set(('path', 'type', 'size'))