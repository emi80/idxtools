"""
Add new file to the index using the provided file metadata
(eg. path, type, size, md5...)

Usage: %s_add [options] <metadata>...

Options:
  -u --update  Update information for an existing dataset
"""

import re
from schema import Schema, Use, Optional
from docopt import docopt


def run(index):
    """Add files to the index"""

    # parser args and remove dashes
    args = docopt(__doc__)
    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    # create validation schema
    sch = Schema({
        Optional('update'): Use(bool),
        str: object
    })
    args = sch.validate(args)

    index.lock()
    try:
        infos = args.get("<metadata>")
        update = args.get("update")
        kwargs = {}
        for info in infos:
            match_ = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", info)
            kwargs[match_.group('key')] = match_.group('value')
        index.insert(update=update, **kwargs)
        index.save()
    finally:
        index.release()

if __name__ == '__main__':
    run(index)
