"""
Usage: indexfile_show [options] [-m <meta_data>]

Options:

  -a, --absolute-path    Specify if absolute path should be returned
  -c, --count            Return the number of files/datasets
  -e, --exact            Specifies whether to perform exact match for searches
  -m, --map-keys         Specify if mapping information for key should be used
                         for output
  -t, --tags <tags>      Output only the selected tags in tabular format (no
                         header)
  -o, --output <output>  The output file. [default: stdout]
  -s, --select <query>   Select datasets using query strings. Examples of valid
                         strings are: sex=M and sex=M,lab=CRG
  --header               Output header when selecting tags
"""

import indexfile
from docopt import docopt
from indexfile.cli import *

def run(args):
    import signal
    import re
    absolute = False
    map_keys = False
    exact = False
    type='index'

    absolute = args.get('--absolute-path')
    map_keys = args.get('--map-keys')
    exact = args.get('--exact')
    header = args.get("--header")

    tags=[]
    if args.get('--tags'):
        type = 'tab'
        if args.get('--tags') != 'all':
            tags = args.get("--tags").split(',')

    i = open_index(args)
    i.lock()

    try:
        indices = []
        if args.get('--select'):
            list_sep=':'
            for arg in args.get('--select'):
                queries = arg.split(',')
                kwargs = {}
                for q in queries:
                    m = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", q)
                    kwargs[m.group('key')] = m.group('value')
                    if list_sep in kwargs[m.group('key')]:
                        kwargs[m.group('key')] = m.group('value').split(list_sep)
                indices.append(i.select(absolute=absolute, exact=exact, **kwargs))
        else:
            indices.append(i)

        for index in indices:
            if isinstance(index,Index):
                if args.get('--count') and not args.get('--tags'):
                    args.get('--output').write("%s%s" % (index.size,os.linesep))
                    return
                signal.signal(signal.SIGPIPE, signal.SIG_DFL)
                command = "index.export(header=%s,type=%r,tags=tags,absolute=absolute" % (header,type)
                if not map_keys:
                    command = "%s,map=None" % command
                command = "%s)" % command
                indexp = eval(command)
                if args.get('--count'):
                    args.get('--output').write("%s%s" % (len(indexp),os.linesep))
                    return
                for line in indexp:
                    args.get('--output').write('%s%s' % (line,os.linesep))
    finally:
        i.release()

if __name__ == '__main__':
    args = docopt(__doc__)
    run(args)
