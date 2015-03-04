"""
Remove files and/or datasets from the index. Query can be a file path or a string
like 'id=ID001' or 'type=bam'.

Usage: %s [options] <query>...

Options:

  -c, --clear  Remove a dataset entry in the index if it does not contain any
               more files [default: false]

"""
from docopt import docopt
from schema import Schema, Use, Optional

# set command info
name = __name__.replace('indexfile_','')
desc = "Remove files from the index"
aliases = ['rm']

def run(index):
    """Remove files and/or datasets from the index"""

    # parser args and remove dashes
    args = docopt(__doc__ % command)
    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    # create validation schema
    sch = Schema({
        Optional('clear'): Use(bool),
        str: object
    })
    args = sch.validate(args)

    index.lock()
    paths = args.get('<query>')
    for path in paths:
        if '=' in path:
            kwargs = dict([path.split('=')])
            index.remove(**kwargs)
        else:
            index.remove(path=path, clear=args.get('clear'))
        index.save()

if __name__ == '__main__':
    run(index)
