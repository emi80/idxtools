"""
Add new file to the index using the provided file metadata (eg. path, type, size, md5...)

Usage: %s_add [options] <metadata>...

Options:
  -u --update  Update information for an existing dataset
"""

from docopt import docopt
from indexfile.cli import *

def run(args, index):
    args = validate(args)

    index.lock()
    try:
        infos = args.get("<metadata>")
        update = args.get("--update")
        kwargs = {}
        for info in infos:
            m = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", info)
            kwargs[m.group('key')] = m.group('value')
        index.insert(update=update, **kwargs)
        index.save()
    finally:
        index.release()

if __name__ == '__main__':
    args = docopt(__doc__)
    run(args, index)
