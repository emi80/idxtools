"""
Usage: %s_remove [options] <path>... [--clear]

Options:

  --clear                   Clear all metadata when <file_path> is the last file of the dataset [default: false]

"""
from docopt import docopt
from schema import Schema, Use, Optional


def run(index):
    """Remove files and/or datasets from the index"""

    # parser args and remove dashes
    args = docopt(__doc__)
    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    # create validation schema
    sch = Schema({
        Optional('clear'): Use(bool),
        str: object
    })
    args = sch.validate(args)

    index.lock()
    paths = args.get('<path>')
    try:
        for path in paths:
            if '=' in path:
                kwargs = dict([path.split('=')])
                index.remove(**kwargs)
            else:
                index.remove(path=path, clear=args.get('clear'))
            index.save()
    finally:
        index.release()

if __name__ == '__main__':
    run(index)
