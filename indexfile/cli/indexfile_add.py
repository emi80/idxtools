"""
Usage: %s_add [options] -m <metadata>

Options:

  -u --update                  Update information for an existing dataset
  -m, --metadata <metadata>    Information related to the file (eg. path, type,
                               size, md5...)
"""

from docopt import docopt
from indexfile.cli import *

def run(args, index):
    args = validate(args)

    index.lock()
    infos = args.get("--metadata").split(',')
    update = args.get("--update")
    kwargs = {}
    for info in infos:
        m = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", info)
        kwargs[m.group('key')] = m.group('value')
    try:
        index.insert(update=update, **kwargs)
        index.save()
    finally:
        index.release()

if __name__ == '__main__':
    args = docopt(__doc__)
    run(args, index)
