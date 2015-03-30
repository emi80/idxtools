"""Utility methods used in the API"""
import re
import os
import copy

def quote(strings, force=False):
    """Quotes string/s"""
    out = []
    if type(strings) == str:
        strings = [strings]
    for item in strings:
        item = str(item)
        if force or ' ' in item and '\"' not in item:
            item = ('\"%s\"' % item)
        out.append(item)
    return out


def match(src, dest, exact=False, oplist=['>', '!=', '<', '==']):

    if type(src) == list:
        return dest in src

    if type(dest) == int:
        try:
            src = int(src)
            return src == dest
        except ValueError:
            if not src.startswith(tuple(oplist)):
                raise SyntaxError("Invalid sytax: {0}{1}".format(dest, src))
            return eval("{0}{1}".format(dest, src), {"__builtins__": {}})

    if type(dest) == str:
        if exact:
            return src == dest
        cre = re.compile(src)
        if cre.match(dest):
            return True
        else:
            return False
    return False


def map_path(pathd, template):
    """Rename a file given a template string"""
    d = pathd.copy()
    path = d.get('path')
    dirname, basename = (os.path.dirname(path), os.path.basename(path))
    d['dirname'] = dirname
    d['basename'] = basename

    # get extension
    pathsplit = basename.split('.')
    n = 2 if pathsplit[-1] == 'gz' else 1
    d['ext'] = '.'.join(pathsplit[-n:])

    # map path
    d[template] = template.format(**d)

    return d


class DotDict(dict):
    """Extends python dictionary allowing attribute access"""
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for key, val in self.items():
            if type(val) == dict:
                val = DotDict(**val)
            self.__setitem__(key, val)

    def __getattr__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        if type(value) == dict:
            value = DotDict(**value)
        dict.__setitem__(self, key, value)

    def lookup(self, value, exact=False):
        result = []
        for k, v in self.items():
            if isinstance(v, list) and value in v:
                result.append(k)
            if isinstance(v, dict):
                print k, DotDict(v).lookup(value)
                result += ["{0}.{1}".format(k, i)
                           for i in DotDict(v).lookup(value)]
            if v == value:
                result.append(k)

        return result

    def __deepcopy__(self, memo):
        return DotDict(copy.deepcopy(dict(self)))

    __setattr__ = __setitem__
    __delattr__ = dict.__delitem__

