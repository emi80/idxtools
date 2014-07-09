"""Utility methods used in the API"""
import copy
import re

def to_tags(kw_sep=' ', sep='=', trail=';', rep_sep=',', quote=None, **kwargs):
    """Convert a dictionary to a string in index file format"""
    taglist = []
    #for k,v in kwargs.items():
    for key, val in dict(sorted(kwargs.items(), key=lambda k: k[0])).items():
        if type(val) == list:
            val = rep_sep.join([
                quote_tags([key, value])[1] for value in val])
        else:
            val = str(val)
            key, val = quote_tags([key, val])
        taglist.append('%s%s%s%s' % (key, sep, val, trail))
    return kw_sep.join(sorted(taglist))


def quote_tags(strings, force=False):
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
    if exact:
        return src == dest
    if type(dest) == int:
        try:
            src = int(src)
            return src == dest
        except ValueError:
            if not src.startswith(tuple(oplist)):
                raise SyntaxError("Invalid sytax: {0}{1}".format(dest, src))
            return eval("{0}{1}".format(dest, src), {"__builtins__": {}})

    if type(dest) == str:
        cre = re.compile(src)
        if cre.match(dest):
            return True
        else:
            return False
    return False


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

