"""
Command line interface to the IndexFile API
"""
import sys
import os
import csv
import yaml
import indexfile
import simplejson as json
from indexfile.index import Index


def default_config():
    """Return the default configuration"""
    config = {}
    config['loglevel'] = indexfile._log_level
    config['format'] = json.dumps(indexfile.default_format)
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


def open_index(config):
    """Open index file from config dictionary"""

    i = Index()
    if not sys.stdin.isatty():
        index = sys.stdin
    else:
        index = config.get('index')

    idx_format = config.get('format')

    if idx_format:
        try:
            idx_format = open(idx_format, 'r')
            i.format = json.load(idx_format)
        except:
            i.format = json.loads(idx_format)

    try:
        i.open(index)
    except csv.Error:
        index = config.get('index')
        i.open(index)

    return i


def validate(args):
    """Validate command line arguments and remove dashes"""

    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])
    if not args.get('index') or args.get('index') == 'stdin':
        args['index'] = sys.stdin
    if 'output' in args.keys():
        if args.get('output') == 'stdout':
            args['output'] = sys.stdout
        else:
            args['output'] = open(args['output'], 'w+')
    return args
