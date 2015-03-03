"""
Command line interface to the IndexFile API
"""
import sys
import os
import csv
import yaml
import indexfile
import simplejson as json
from os import environ as env
from schema import SchemaError
from indexfile.index import Index

COMMANDS = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'commands.json')))

#COMMANDS = {
#    'show': {
#        'desc': 'Show the index',
#        'aliases': []
#    },
#    'add': {
#        'desc': 'Add file contents to the index',
#        'aliases': []
#    },
#    'remove': {
#        'desc': 'Remove files from the index',
#        'aliases': ['rm']
#    },
#    'help': {
#        'desc': 'Show the help',
#    }
#}

DEFAULT_CONFIG_FILE = '.indexfile.yml'
DEFAULT_ENV_INDEX = 'IDX_FILE'
DEFAULT_ENV_FORMAT = 'IDX_FORMAT'


def walk_up(bottom):
    """
    mimic os.walk, but walk 'up'
    instead of down the directory tree
    """

    bottom = os.path.realpath(bottom)

    #get files in current dir
    try:
        names = os.listdir(bottom)
    except Exception as e:
        print e
        return

    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(bottom, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    yield bottom, dirs, nondirs

    new_path = os.path.realpath(os.path.join(bottom, '..'))

    # see if we are at the top
    if new_path == bottom:
        return

    for x in walk_up(new_path):
        yield x


def get_command_aliases():
    """Get all command aliases"""
    return [alias for command in COMMANDS.values()
            for alias in command.get('aliases', [])]


def get_command(alias):
    """Get command from command string or alias"""
    if alias in COMMANDS:
        return alias
    return [k for k, v in COMMANDS.iteritems()
            if alias in v.get('aliases', [])][0]


def default_config():
    """Return the default configuration"""
    config = {}
    config['loglevel'] = indexfile._log_level
    config['format'] = json.dumps(indexfile.default_format)
    return config


def update_config(config, new_config):
    """Update config with values in new_config"""
    for key, val in new_config.iteritems():
        if key not in config or val not in [None]:
            if type(val) is unicode and val[0] == "$":
                val = os.getenv(val[1:])
            config[key] = val


def load_config(path=None, args=None, use_env=True):
    """Load configuration for a session"""
    config = default_config()
    if use_env:
        if 'IDX_FILE' in env:
            update_config(config, {'index': env.get(DEFAULT_ENV_INDEX)})
        if 'IDX_FORMAT' in env:
            update_config(config, {'format': env.get(DEFAULT_ENV_FORMAT)})
    if path:
        if os.path.isdir(path):
            for c, d, f in walk_up(path):
                if DEFAULT_CONFIG_FILE in f:
                    config_file = os.path.join(c, DEFAULT_CONFIG_FILE)
                    update_config(config, yaml.load(open(config_file)))
                    break
    if args:
        update_config(config, args)
    return config


def open_index(config):
    """Open index file from config dictionary"""

    i = Index()
    index = config.get('index')
    idx_format = config.get('format')

    try:
        i.set_format(idx_format)
        i.open(index)
    except csv.Error:
        index = config.get('index')
        i.open(index)
    except AttributeError:
        pass

    return i


# validation objects
class Command(object):

    def __init__(self, error=None):
        self._error = error

    def validate(self, data):
        """Return valid command string or SchemaException in case of error"""
        if not data:
            data = 'help'
        if data in COMMANDS.keys() + get_command_aliases():
            return data
        else:
            raise SchemaError('Invalid command %r' %
                              data,
                              self._error)
