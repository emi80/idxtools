#!/usr/bin/env python
"""Load index files

Usage:
   idxtools [-hacem] [-t TAGS] [-i INPUT_FILE] [-o OUTPUT_FILE]
            [-f FORMAT] [-s QUERY_STRING]...
            [<command> [<args>...]]

Options:
  -h --help                                Show this help message and exit
  -a --absolute-path                       Specify if absolute path should be returned
  -c --count                               Return the number of files/datasets
  -e --exact                               Specifies whether to perform exact match for searches
  -m --map-keys                            Specify if mapping information for key should be used for output
  -t TAGS, --tags TAGS                     Output only the selected tags in tabular format (no header)
  -i INPUT_FILE, --input INPUT_FILE        The input index file. [default: stdin]
  -o OUTPUT_FILE, --output OUTPUT_FILE     The output file. [default: stdout]
  -f FORMAT, --format FORMAT               Index format specifications in JSON format.
                                           Can be a file or a string.
  -s QUERY_STRING, --select QUERY_STRING   Select datasets using query strings.
                                           Examples of valid strings are: sex=M and sex=M,lab=CRG

"""
from indexfile.index import *
from docopt import docopt

import os

class AddCommand(object):
    """Add files

    Usage:
       idxtools add [-hu] [-i INDEX_FILE] [-f FORMAT] -m FILE_INFO

    Options:
      -h --help                           Show this help message and exit
      -u --update                         Update information for an existing dataset
      -i INPUT_FILE, --input INPUT_FILE   The input index file. [default: stdin]
      -f FORMAT, --format FORMAT          Index format specifications in JSON format.
                                          Can be a file or a string.
      -m METADATA, --metadata METADATA    Information related to the file (eg. path, type, size, md5...)

    """

    def run(self, argv):
        args = docopt(self.__doc__, argv=argv)
        args = validate(args)
        i = open_index(args)
        i.lock()
        infos = args.get("--metadata").split(',')
        update = args.get("--update")
        kwargs = {}
        for info in infos:
            m = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", info)
            kwargs[m.group('key')] = m.group('value')
        try:
            i.insert(update=update, **kwargs)
            i.save()
        finally:
            i.release()


class RemoveCommand(object):
    """Remove files

    Usage:
       idxtools rm [-h] [-i INDEX_FILE] [-f FORMAT] -p FILE_PATH

    Options:
      -h --help                           Show this help message and exit
      -i INPUT_FILE, --input INPUT_FILE   The input index file. [deafult: stdin]
      -f FORMAT, --format FORMAT          Index format specifications in JSON format.
                                          Can be a file or a string.
      -p FILE_PATH, --path FILE_PATH      The path of the file to be removed

    """

    def run(self, argv):
        args = docopt(self.__doc__, argv=argv)
        args = validate(args)
        i = open_index(args)
        i.lock()
        path = args.get('--path')
        try:
            i.remove(path=path)
            i.save()
        finally:
            i.release()


def open_index(args):
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

def run(args):
    import json
    import signal
    import re
    absolute = False
    map_keys = False
    exact = False
    type='index'

    if args.get('--absolute-path'):
        absolute = True
    if args.get('--map-keys'):
        map_keys = True
    if args.get('--exact'):
        exact = True

    tags=[]
    if args.get("--tags"):
        type = 'tab'
        tags = args.get("--tags").split(',')

    i = open_index(args)
    i.lock()

    try:
        indices = []
        if args.get('--select'):
            list_sep=':'
            for arg in args.get('--select'):
                queries = arg.split(',')
                kwargs = {}
                for q in queries:
                    m = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", q)
                    kwargs[m.group('key')] = m.group('value')
                    if list_sep in kwargs[m.group('key')]:
                        kwargs[m.group('key')] = m.group('value').split(list_sep)
                indices.append(i.select(absolute=absolute, exact=exact, **kwargs))
        else:
            indices.append(i)

        for index in indices:
            if isinstance(index,Index):
                if args.get('--count') and not args.get('--tags'):
                    args.get('--output').write("%s%s" % (index.size,os.linesep))
                    return
                signal.signal(signal.SIGPIPE, signal.SIG_DFL)
                command = "index.export(type=%r,tags=tags,absolute=absolute" % type
                if not map_keys:
                    command = "%s,map=None" % command
                command = "%s)" % command
                indexp = eval(command)
                if args.get('--count'):
                    args.get('--output').write("%s%s" % (len(indexp),os.linesep))
                    return
                for line in indexp:
                    args.get('--output').write('%s%s' % (line,os.linesep))
    finally:
        i.release()

def validate(args):
    if not args.get('--input') or args.get('--input') =='stdin':
        args['--input'] = sys.stdin
    if '--output' in args.keys():
        if args.get('--output') == 'stdout':
            args['--output'] = sys.stdout
        else:
            args['--output'] = open(args['--output'],'w+')
    return args


def main():
    import warnings
    warnings.simplefilter('ignore')

    args = docopt(__doc__, version='IndexFile 0.9-alpha',options_first=True)

    if args.get('<command>'):
        argv = [args.get('<command>')] + args.get('<args>')
        if args.get('<command>') == 'add':
            c = AddCommand().run(argv)
            sys.exit(0)
        if args.get('<command>') == 'rm':
            c = RemoveCommand().run(argv)
            sys.exit(0)
    args = validate(args)
    run(args)
