"""
Usage: %s add [options] -m <metadata>

Options:

  -u --update                  Update information for an existing dataset
  -m, --metadata <metadata>    Information related to the file (eg. path, type,
                               size, md5...)
"""

from docopt import docopt
import indexfile

def run(self, argv):
    args = docopt(self.__doc__, argv=argv)
    args = validate(args)
    i = open_index(args)
    i.lock()
    infos = args.get("--metadata").split(',')
    update = args.get("--update")
    kwargs = {}
    for info in infos:
        m = re.match("(?P<key>[^=<>!]*)=(?P<value>.*)", info)
        kwargs[m.group('key')] = m.group('value')
    try:
        i.insert(update=update, **kwargs)
        i.save()
    finally:
        i.release()

if __name__ == '__main__':
    print docopt(__doc__ % indexfile.__name__)
