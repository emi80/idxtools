#!/usr/bin/env python
from indexfile.index import *

def main(args):
    import os
    import json
    import signal
    i = Index()
    if args.format:
        try:
            format = open(args.format,'r')
            i.format = json.load(format)
        except:
            i.format = json.loads(args.format)
    i.open(args.input)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    for line in i.export():
        args.output.write('%s%s' % (line,os.linesep))

if __name__ == "__main__":
    import argparse
    import warnings
    warnings.simplefilter('ignore')
    parser = argparse.ArgumentParser(description='Load index files.')
    parser.add_argument('-i', '--input', nargs='?', type=argparse.FileType('r'), default=sys.stdin,metavar='<input_file>', help='open file')
    parser.add_argument('-o', '--output', nargs='?', type=argparse.FileType('w'), default=sys.stdout, metavar='<output_file>', help='export to file')
    parser.add_argument('-f', '--format', nargs='?', default=None, metavar='<format_file>', help='index format specs in json')

    args = parser.parse_args()
    main(args)


