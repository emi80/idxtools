"""
Command line interface to the IndexFile API
"""
from indexfile.index import *
import os

def open_index(args):
    import simplejson as json

    i = Index()
    format = args.get('--format')
    index = args.get('--input')

    if not format:
        format = os.environ.get('IDX_FORMAT')

    if format:
        try:
            format = open(format,'r')
            i.format = json.load(format)
        except:
            i.format = json.loads(format)

    if index is sys.stdin and os.environ.get('IDX_FILE'):
        index = os.environ.get('IDX_FILE')

    i.open(index)

    return i

def validate(args):
    if not args.get('--input') or args.get('--input') =='stdin':
        args['--input'] = sys.stdin
    if '--output' in args.keys():
        if args.get('--output') == 'stdout':
            args['--output'] = sys.stdout
        else:
            args['--output'] = open(args['--output'],'w+')
    return args
