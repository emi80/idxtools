#! /usr/bin/env python
"""

Usage: %s [--loglevel <loglevel>] [-i <index>] [-f <format>] <command> [<args>...]
       %s [--version] [--help]

Options:
  -h, --help             Show this help message
  --version              Show the version information
  --loglevel <level>     Set the log level to one of error|warn|info|debug
  -i, --input <index>    The input index file. [default: stdin]
  -f, --format <format>  Index format specifications in JSON format. Can be a
                         file or a string.

The main commands are:

  show       Show the index
  add        Add file contents to the index
  remove     Remove files from the index

"""
import sys
from subprocess import call
from docopt import docopt
from indexfile.cli import *

def main():
    import indexfile
    import warnings
    warnings.simplefilter('ignore')
    name = indexfile.__name__
    version = indexfile.__version__

    args = docopt(__doc__ % (name,name), version="%s v%s" % (name, version), options_first=True)

    args = validate(args)

    index = open_index(args)

    argv = [args['<command>']] + args['<args>']
    if args['<command>'] in 'show add remove'.split():
        import runpy
        if len(argv) == 1 and args['<command>'] != "show":
            argv.append('--help')
        sys.argv = argv
        runpy.run_module("indexfile.cli.indexfile_%s" % args['<command>'], run_name="__main__",
          init_globals={'index':index})
    elif args['<command>'] in ['help', None]:
        docopt(__doc__ % (name,name), version="%s v%s" %
        (name,version), argv=['--help'])
    else:
        exit("%r is not an indexfile command. See '%s help'." %
        (args['<command>'],name))

if __name__ == '__main__':
    main()
