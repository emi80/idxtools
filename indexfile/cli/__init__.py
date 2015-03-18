"""
Command line interface to the IndexFile API
"""
import sys
import os
import csv
import imp
import yaml
import glob
import indexfile
import simplejson as json
from os import environ as env
from schema import SchemaError
from indexfile.index import Index

DEFAULT_CONFIG_FILE = '.indexfile.yml'
DEFAULT_ENV_INDEX = 'IDX_FILE'
DEFAULT_ENV_FORMAT = 'IDX_FORMAT'

IGNORE_COMMANDS = ['__init__', 'indexfile_main']

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


def load_commands():
    """Load commands from files"""
    basedir = os.path.dirname(__file__)
    cmds = glob.glob('{0}/*.py'.format(basedir))
    d = {}

    for cmd in cmds:
        mod = os.path.basename(cmd).replace('.py', '')
        if mod in IGNORE_COMMANDS:
            continue
        info = imp.find_module(mod, [basedir])
        m = imp.load_module(mod, *info)
        d[m.name] = {'desc': m.desc, 'aliases': m.aliases}

    d['help'] = {'desc': "Show the help"}

    return d


def get_command_aliases(cmds):
    """Get all command aliases"""
    return [alias for command in cmds.values()
            for alias in command.get('aliases', [])]


def get_command(alias, cmds):
    """Get command from command string or alias"""
    if alias in cmds:
        return alias
    return [k for k, v in cmds.iteritems()
            if alias in v.get('aliases', [])][0]


def get_commands_help(cmds):
    """Get list of commands and descriptions for the help message"""
    s = []
    m = 0
    for k, v in cmds.iteritems():
        if v.get('aliases'):
            k = k + " ({0})".format(', '.join(v.get('aliases')))
        m = max(m, len(k))
        s.append([k, v.get('desc', "")])
    return '\n'.join(['  {0}\t{1}'.format(name.ljust(m), desc) for name, desc in s])


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
        if DEFAULT_ENV_INDEX in env:
            update_config(config, {'index': env.get(DEFAULT_ENV_INDEX)})
        if DEFAULT_ENV_FORMAT in env:
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

    def __init__(self, error=None, commands=None):
        self._error = error
        self._commands = commands

    def validate(self, data):
        """Return valid command string or SchemaException in case of error"""
        if not data:
            data = 'help'
        if data in self._commands.keys() + get_command_aliases(self._commands):
            return data
        else:
            raise SchemaError('Invalid command %r' %
                              data,
                              self._error)
