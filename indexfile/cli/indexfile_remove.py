"""
Usage: %s remove [options] -p FILE_PATH

Options:

  -p, --path <file_path>    The path of the file to be removed

"""
from docopt import docopt
import indexfile

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

if __name__ == '__main__':
    print docopt(__doc__ % indexfile.__name__)
