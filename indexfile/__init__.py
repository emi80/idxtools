"""The indexfile package
"""
from .logger import get_logger, set_loglevel, log_levels
from .config import config, OUTPUT_FORMATS, MergeTypes
from .dataset import Dataset
from .index import Index

__all__ = [
    # config
    'config', 'OUTPUT_FORMATS', 'MergeTypes',
    # dataset
    'Dataset',
    # index
    'Index',
    # logger
    'get_logger', 'set_loglevel', 'log_levels'
]

__name__ = "idxtools"
__version__ = "0.12.2.dev1"
