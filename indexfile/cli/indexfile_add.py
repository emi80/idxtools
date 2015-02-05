"""
Add new file to the index using the provided file metadata
(eg. path, type, size, md5...)

Usage: %s_add [options] [<metadata>...]

Options:
  -a --attributes <attributes>  List of attribute name referring to the file
                                list.
  -l --file-list <list>         List of files to be added
  -u --update                   Update information for an existing dataset
  -f --force                    Only works in combination with --update. Add non-existing keys to the dataset.
"""

import re
import sys
import indexfile
from schema import Schema, Use, Optional, Or, And
from docopt import docopt


def run(index):
    """Add files to the index"""
    log = indexfile.getLogger(__name__)

    # parser args and remove dashes
    args = docopt(__doc__)
    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    # create validation schema
    sch = Schema({
        'filelist': Or(None,
                       And(Or('-', 'stdin'),
                       Use(lambda x: sys.stdin)),
                       Use(open)),
        'attributes': Or(And(None, Use(lambda x: "")), str),
        Optional('update'): Use(bool),
        Optional('force'): Use(bool),
        str: object
    })
    args = sch.validate(args)

    index.lock()

    try:
        header = args.get('attributes').split(",")
        filelist = args.get('filelist')
        infos = args.get("<metadata>")
        update = args.get("update")
        force = args.get("force")
        kwargs = {}
        if not infos and filelist:
            for file_ in filelist.readlines():
                file_ = file_.split()
                assert len(file_) == len(header)
                for i, k in enumerate(header):
                    kwargs[k] = file_[i]
                index.insert(update=update, addkeys=force, **kwargs)
            index.save()
        elif infos:
            for info in infos:
                match_ = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", info)
                kwargs[match_.group('key')] = match_.group('value')
            index.insert(update=update, **kwargs)
            index.save()
        else:
            log.warn("Nothing to do")
    finally:
        index.release()

if __name__ == '__main__':
    run(index)
