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
from indexfile.index import Index


def default_config():
    """Return the default configuration"""
    config = {}
    config['loglevel'] = indexfile._log_level
    config['format'] = json.dumps(indexfile.default_format)
    return config


def update_config(config, new_config):
    """Update config with values in new_config"""
    for key, val in new_config.iteritems():
        if key not in config or val not in [None, sys.stdin, sys.stdout]:
            if type(val) is unicode and val[0] == "$":
                val = os.getenv(val[1:])
            config[key] = val


def load_config(path=None, args=None, use_env=True):
    """Load configuration for a session"""
    config = default_config()
    if use_env:
        if 'IDX_FILE' in env:
            update_config(config, {'index': env.get('IDX_FILE')})
        if 'IDX_FORMAT' in env:
            update_config(config, {'format': env.get('IDX_FORMAT')})
    if path:
        config_file = path
        if os.path.isdir(path):
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

    try:
        i.set_format(idx_format)
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
