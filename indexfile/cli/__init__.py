"""
Command line interface to the IndexFile API
"""
import sys
import csv
import simplejson as json
from indexfile.index import Index


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
