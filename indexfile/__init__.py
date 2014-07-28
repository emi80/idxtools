"""The indexfile package

"""

import logging

__name__ = "idxtools"
__version__ = "0.10.0"
_log_level = 30

# default format

default_format = {
    "colsep": "\t",
    "fileinfo": [
        "path",
        "size",
        "md5",
        "type",
        "view"
    ],
    "kw_sep": " ",
    "rep_sep": ",",
    "sep": "=",
    "trail": ";"
}


def getLogger(name):
    """Return the logger given the name"""
    logger = logging.getLogger(name)
    logger.handler = []
    return logger


def setLogLevel(level):
    """Set logger loglevel"""
    log.setLevel(getattr(logging, str(level).upper(), 30))

log = logging.getLogger()
log.handler = []
log.propagate = False
setLogLevel(_log_level)

ch = logging.StreamHandler()
fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s', '%m/%d/%Y %H:%M:%S')
ch.setFormatter(fmt)
log.addHandler(ch)
