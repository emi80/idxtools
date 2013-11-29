"""
Usage: %s add [options] -m <metadata>

Options:

  -u --update                  Update information for an existing dataset
  -m, --metadata <metadata>    Information related to the file (eg. path, type,
                               size, md5...)
"""

from docopt import docopt
import indexfile

if __name__ == '__main__':
    print docopt(__doc__ % indexfile.__name__)
