#!/usr/bin/env python
"""Load index files

Usage:
   %s [-h] [-a] [-m] [-c] [-i <input_file>] [-o <output_file>]
                 [-f <format_file>] [-s <query_string>]...

Options:
  -h --help  show this help message and exit
  -i <input_file>, --input <input_file>  open file
  -o <output_file>, --output <output_file>  export to file
  -f <format_file>, --format <format_file>  index format specs in json
  -a --absolute-path  specify if absolute path should be returned
  -m --map-keys  specify if mapping information for key should be used for output
  -c --count  return the number of files/datasets
  -s <query_string>, --select <query_string>  select datasets using query strings.
                                              Examples of valid strings are: sex=M and sex=M,lab=CRG

"""
from indexfile.index import *
from docopt import docopt

import os
__doc__ %= "idxtools"

def run(args):
    import json
    import signal
    import re
    absolute = False
    map_keys = False
    if args.get('--absolute-path'):
        absolute = True
    if args.get('--map-keys'):
        map_keys = True

    i = Index()
    if args.get('--format'):
        try:
            format = open(args.get('--format'),'r')
            i.format = json.load(format)
        except:
            i.format = json.loads(args.get('--format'))
    i.open(args.get('--input'))

    if args.get('--select'):
        indices = []
        for arg in args.get('--select'):
            queries = arg.split(',')
            kwargs = {}
            for q in queries:
                m = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", q)
                kwargs[m.group('key')] = m.group('value')
            indices.append(i.select(absolute=absolute, **kwargs))

    for index in indices:
        if isinstance(index,Index):
            if args.get('--count'):
                args.get('--output').write("%s%s" % (index.size,os.linesep))
                return
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
            command = "index.export(absolute=absolute"
            if not map_keys:
                command = "%s,map=None" % command
            command = "%s)" % command
            for line in eval(command):
                args.get('--output').write('%s%s' % (line,os.linesep))
        else:
            if  args.get('--count'):
                args.get('--output').write("%s%s" % (len(index),os.linesep))
                return
            for line in index:
                args.get('--output').write('%s%s' % (line,os.linesep))

def main():
    import warnings
    warnings.simplefilter('ignore')

    args = docopt(__doc__, version='IndexFile 0.9-alpha')
    if not args.get('--input'):
        args['--input'] = sys.stdin
    if not args.get('--output'):
        args['--output'] = sys.stdout
    else:
        args['--output'] = open(args['--output'],'w+')
    run(args)


