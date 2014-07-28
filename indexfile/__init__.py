"""The indexfile package

"""

import logging
import os
import yaml
import json
import sys

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


def default_config():
    """Return the default configuration"""
    config = {}
    config['loglevel'] = _log_level
    config['format'] = json.dumps(default_format)
    return config


def update_config(config, new_config):
    """Update config with values in new_config"""
    for k, v in new_config.iteritems():
            if k not in config or v not in [None, sys.stdin, sys.stdout]:
                if type(v) is unicode and v[0] == "$":
                    v = os.getenv(v[1:])
                config[k] = v



def load_config(path, args=None):
    """Load configuration for a session"""
    config = default_config()
    config_file = os.path.join(path, 'indexfile.yml')
    if os.path.exists(config_file):
        update_config(config, yaml.load(open(config_file)))
    if args:
        update_config(config, args)
    return config


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
