#! /usr/bin/env python
"""

Usage: %s [-i <index>] [-f <format>] [--loglevel <loglevel>] [<command>]
          [<args>...] %s [--version] [--help]

Options:
  -h, --help             Show this help message
  --version              Show the version information
  --loglevel <level>     Set the log level to one of error|warn|info|debug
  -i, --index <index>    The input index file.
  -f, --format <format>  Index format specifications in JSON format. Can be a
                         file or a string.

The main commands are:

  show       Show the index
  add        Add file contents to the index
  remove     Remove files from the index

"""
import sys
import os
import runpy
import indexfile
from docopt import docopt
from schema import Schema, And, Or, Use, Optional
from indexfile.cli import open_index, load_config, Command, get_command


def main():
    """
    Main function
    """
    name = indexfile.__name__
    version = indexfile.__version__
    log = indexfile.getLogger(__name__)

    # create validation schema
    sch = Schema({
        'index': Or(None,
                    And(Or('-', 'stdin'),
                        Use(lambda x: sys.stdin)),
                    open),
        Optional('format'): open,
        Optional('loglevel'): And(str,
                                  Use(str.lower),
                                  Or('error',
                                     'warn',
                                     'info',
                                     'debug')),
        '<command>': Command(),
        str: object
    })

    # parse args and remove dashes
    args = docopt(__doc__ % (name, name), version="%s v%s" % (name, version),
                  options_first=True)
    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    # validate args
    args = sch.validate(args)

    # deal with 'help' command
    if args.get('<command>') == 'help':
        docopt(__doc__ % (name, name),
               version="%s v%s" % (name, version), argv=['--help'])

    # load the index and delegate command
    config = load_config(os.getcwd(), args)

    indexfile.setLogLevel(config.get('loglevel'))
    index = open_index(config)

    command_ = get_command(args.get('<command>'))
    argv = [command_] + args['<args>']
    sys.argv = argv
    module_ = "indexfile.cli.indexfile_%s" % command_
    runpy.run_module(module_,
                     run_name="__main__",
                     init_globals={'index': index})


if __name__ == '__main__':
    # execute main function
    main()
