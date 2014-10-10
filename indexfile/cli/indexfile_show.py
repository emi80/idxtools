"""
Usage: indexfile_show [options] [<query>]...

Select datasets using query strings. Examples of valid strings are: 'sex=M' and 'lab=CRG'.
Multiple fields in a query are joind with an 'AND'.

Options:

  -a, --absolute-path    Specify if absolute path should be returned
  -c, --count            Return the number of files/datasets
  -e, --exact            Specifies whether to perform exact match for searches
  -m, --map-keys         Specify if mapping information for key should be used
                         for output
  -t, --tags <tags>      Output only the selected tags in tabular format (no
                         header)
  -s, --show-missing     Show lines with missing values [default:
                         false]
  -o, --output <output>  The output file. [default: stdout]
  --header               Output header when selecting tags
"""
import os
import signal
import re
import sys
from schema import Schema, And, Or, Use, Optional
from docopt import docopt
from indexfile.index import Index


def run(index):
    """Show index contents and filter based on query terms"""
    export_type = 'index'

    # parser args and remove dashes
    args = docopt(__doc__)
    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    # create validation schema
    sch = Schema({
        Optional('absolutepath'): Use(bool),
        Optional('count'): Use(bool),
        Optional('exact'): Use(bool),
        Optional('mapkeys'): Use(bool),
        Optional('tags'): str,
        Optional('showmissing'): Use(bool),
        'output': Or(None,
                     And(Or('-', 'stdout'),
                         Use(lambda x: sys.stdout)),
                     Use(lambda f: open(f, 'w+'))),
        Optional('header'): Use(bool),
        str: object
    })
    args = sch.validate(args)

    absolute = args.get('absolutepath')
    map_keys = args.get('mapkeys')
    exact = args.get('exact')
    header = args.get("header")
    hide_missing = not args.get("showmissing")

    tags = []
    if args.get('tags'):
        export_type = 'tab'
        if args.get('tags') != 'all':
            tags = args.get("tags").split(',')

    index.lock()

    try:
        indices = []
        query = args.get('<query>')
        if query:
            list_sep = ':'
            kwargs = {}
            for qry in query:
                match = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", qry)
                kwargs[match.group('key')] = match.group('value')
                if list_sep in kwargs[match.group('key')]:
                    kwargs[match.group('key')] = match.group(
                        'value').split(list_sep)
            indices.append(index.lookup(exact=exact, **kwargs))
        else:
            indices.append(index)

        for i in indices:
            if isinstance(i, Index):
                if args.get('count') and not args.get('tags'):
                    args.get('output').write("%s%s" % (len(i), os.linesep))
                    return
                signal.signal(signal.SIGPIPE, signal.SIG_DFL)
                kwargs = {
                    'header': header,
                    'export_type': export_type,
                    'tags': tags,
                    'absolute': absolute,
                    'hide_missing': hide_missing
                }
                if not map_keys:
                    kwargs['map'] = None
                indexp = i.export(**kwargs)
                if args.get('count'):
                    args.get('output').write("%s%s" % (len(indexp), os.linesep))
                    return
                for line in indexp:
                    args.get('output').write('%s%s' % (line, os.linesep))

    except Exception:
        if args.get('output') != sys.stdout:
            os.remove(ags.get('output').name)

    finally:
        index.release()

if __name__ == '__main__':
    run(index)
