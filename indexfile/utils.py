"""Utility methods used in the API"""

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


class DotDict(dict):
    """Extends python dictionary allowing attribute access"""
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            self[key] = val

    def __getattr__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        if type(value) == dict:
            value = DotDict(**value)
        dict.__setitem__(self, key, value)

    __setattr__ = __setitem__
    __delattr__ = dict.__delitem__
