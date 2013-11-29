"""
Usage: %s remove [options] -p FILE_PATH

Options:

  -p, --path <file_path>    The path of the file to be removed

"""
from docopt import docopt
import indexfile

if __name__ == '__main__':
    print docopt(__doc__ % indexfile.__name__)
