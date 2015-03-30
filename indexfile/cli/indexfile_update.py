"""
Add or update metadata information to the index

Usage: %s [options] [<metadata>...]

Options:
  -l --metadata-list <list>     List of metadata information to be used.
  -a --attributes <attributes>  List of attribute names referring to the metadata
                                list.
  -u --update                   Update information for existing datasets
  -f --force                    Only works in combination with --update. Add non-existing keys to the dataset.
"""

import re
import sys
import indexfile
from schema import Schema, Use, Optional, Or, And
from docopt import docopt

# set command info
name = __name__.replace('indexfile_','')
desc = "Add or update file/dataset metadata to the index"
aliases = ['add']

def run(index):
    """Add or update metadata information to the index"""
    log = indexfile.getLogger(__name__)

    # parser args and remove dashes
    args = docopt(__doc__ % command)
    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    # create validation schema
    sch = Schema({
        'metadatalist': Or(None,
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

    header = args.get('attributes').split(",")
    mdlist = args.get('metadatalist')
    infos = args.get("<metadata>")
    update = args.get("update")
    force = args.get("force")
    kwargs = {}
    if not infos and mdlist:
        for file_ in mdlist.readlines():
            file_ = file_.strip().split('\t')
            assert len(file_) == len(header), "The number of attributes in the metadata list is different from the one given in the command line"
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
        docopt(__doc__ % command, argv='--help')

if __name__ == '__main__':
    run(index)
