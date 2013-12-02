"""
Usage: %s_remove [options] -p FILE_PATH

Options:

  -p, --path <file_path>    The path of the file to be removed

"""
from docopt import docopt
from indexfile.cli import *

def run(args, index):
    args = validate(args)

    index.lock()
    path = args.get('--path')
    try:
        index.remove(path=path)
        index.save()
    finally:
        index.release()

if __name__ == '__main__':
    args = docopt(__doc__)
    run(args, index)
