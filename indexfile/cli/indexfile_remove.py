"""
Usage: %s_remove [options] <path>... [--clear]

Options:

  --clear                   Clear all metadata when <file_path> is the last file of the dataset [default: false]

"""
from docopt import docopt
from indexfile.cli import *

def run(args, index):
    args = validate(args)

    index.lock()
    paths = args.get('<path>')
    try:
        for path in paths:
            index.remove(path=path, clear=args.get('--clear'))
            index.save()
    finally:
        index.release()

if __name__ == '__main__':
    args = docopt(__doc__)
    run(args, index)
