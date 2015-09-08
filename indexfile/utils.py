"""Utility methods used in the API"""
import re
import os
import copy
import operator

op_map = {
    '==': 'eq', '=':  'eq', 'eq': 'eq',
    '<':  'lt', 'lt': 'lt',
    '<=': 'le', 'le': 'le',
    '>':  'gt', 'gt': 'gt',
    '>=': 'ge', 'ge': 'ge',
    '!=': 'ne', '<>': 'ne', 'ne': 'ne'
}

def quote(strings, force=False):
    """Quotes string/s"""
    out = []
    if not isinstance(strings, list):
        strings = [strings]
    for item in strings:
        item = str(item)
        if force or ' ' in item and '"' not in item:
            item = ('"%s"' % item)
        out.append(item)
    return out


def match(src, dest, exact=False, match_all=False):
    """Match pattern from src to dst"""

    if exact:
        return src == dest
    else:
        try:
            op_re = re.compile("(?P<op>[<>=!]+)(?P<number>[0-9]+)")
            op_match = op_re.search(src)
            if op_match:
                op = getattr(operator, op_map[op_match.group('op')])
                if not isinstance(dest, list):
                    dest = [dest]      
                src = int(op_match.group('number'))
                dest = [int(x) for x in dest]
                result = [op(d, src) for d in dest]
            else:
                src_re = re.compile(src)
                if not isinstance(dest, list):
                    dest = [dest]
                result = [bool(src_re.search(d)) for d in dest]
            if match_all:
                return all(result)
            return True in result
        except KeyError:
            raise SyntaxError('Unrecognized {}. Operator must be one of: {}.'.format(
                repr(op_match.group('op')), ' '.join(op_map.keys())))
        except (TypeError, ValueError):
            if not isinstance(dest, list):
                    dest = [dest]  
            return src in dest


def get_file_type(file_path):
    """Get file type from file extension"""
    file_name, file_type = [s.strip('.') for s in os.path.splitext(file_path)]
    if file_type == 'gz':
        file_type = os.path.splitext(file_name)[1].strip('.')
    return file_type


def render(info, template):
    """Render a template string given some information"""
    # add some file information
    d = info.copy()
    path = d.get('path')
    # dirname and basename
    dirname, basename = (os.path.dirname(path), os.path.basename(path))
    d['dirname'] = dirname
    d['basename'] = basename
    # extension
    pathsplit = basename.split('.')
    n = 2 if pathsplit[-1] == 'gz' else 1
    d['ext'] = '.'.join(pathsplit[-n:])

    # render template
    d[template] = template.format(**d)

    return d


class DotDict(dict):
    """Extends python dictionary allowing attribute access"""
    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)

        for key, val in self.iteritems():
            if isinstance(val, dict):
                self[key] = DotDict(val)

    def __getattr__(self, name):
        if name in self:
            return self.get(name)
        raise AttributeError('%r object has no attribute %r' % (
                                 self.__class__.__name__, name))


    def __setitem__(self, key, value):
        if type(value) == dict:
            value = DotDict(**value)
        dict.__setitem__(self, key, value)


    def update(self, other=None, **kwargs):
        """Update a DotDict supporting nested attribute access"""
        other = other or []
        if type(other) == dict:
            other = DotDict(other)
        kwargs = DotDict(kwargs)
        for k, v in kwargs.iteritems():
            if isinstance(v, dict):
                kwargs[k] = self.get(k, {})
                kwargs[k].update(v)
        # call update from superclass
        super(DotDict, self).update(other, **kwargs)


    def lookup(self, value, exact=False):
        result = []
        for k, v in self.items():
            if isinstance(v, list) and value in v:
                result.append(k)
            if isinstance(v, dict):
                result += ["{0}.{1}".format(k, i)
                           for i in DotDict(v).lookup(value)]
            if v == value:
                result.append(k)

        return result

    def __deepcopy__(self, memo):
        return DotDict(copy.deepcopy(dict(self), memo))

    __setattr__ = __setitem__
    __delattr__ = dict.__delitem__

