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

   add        Add file contents to the index
   remove     Remove files from the index

"""
import sys
from subprocess import call
from docopt import docopt

def main():
  import indexfile
  import warnings
  warnings.simplefilter('ignore')
  name = indexfile.__name__

  args = docopt(__doc__ % (name,name), version="idxtools v%s" % indexfile.__version__,options_first=True)

  argv = [args['<command>']] + args['<args>']
  if args['<command>'] in 'show add remove'.split():
      import runpy
      sys.argv = argv
      runpy.run_module("indexfile.cli.indexfile_%s" % args['<command>'], run_name="__main__")
  elif args['<command>'] in ['help', None]:
      exit(call(['python', 'indexfile_main.py', '--help']))
  else:
      exit("%r is not an indexfile command. See 'git help'." % args['<command>'])

if __name__ == '__main__':
  main()
