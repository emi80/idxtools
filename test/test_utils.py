"""Test utility methods"""

from indexfile import utils as u
from copy import deepcopy

def test_to_tags():
    """Convert dictionary to indexfile string"""
    info = {'id': '1', 'path': 'test.txt', 'view': 'text', 'type': 'txt'}
    # Disable warning about * magic
    # pylint: disable=W0142
    out = u.to_tags(**info)
    # pylint: enable=W0142
    assert out == "id=1; path=test.txt; type=txt; view=text;"


def test_to_tags_rep():
    """Convert dictionary to indexfile string"""
    info = {'id': ['1', '2'], 'path': ['test1.txt', 'test2.txt'],
            'view': ['text', 'text'], 'type': ['txt', 'txt']}
    # Disable warning about * magic
    # pylint: disable=W0142
    out = u.to_tags(**info)
    # pylint: enable=W0142
    assert out == '''id=1,2; path=test1.txt,test2.txt; type=txt,txt; view=text,text;'''


def test_quote_key():
    """Test quote key"""
    key = "Long key with space"
    val = "1"
    qkey, qval = u.quote_tags([key, val])
    assert qkey == '"Long key with space"'
    assert qval == "1"


def test_quote_val():
    """Test quote value"""
    key = "1"
    val = "Long value with space"
    qkey, qval = u.quote_tags([key, val])
    assert qkey == "1"
    assert qval == '"Long value with space"'


def test_quote_int():
    """Test quote integer value"""
    key = 1
    val = 10
    qkey, qval = u.quote_tags([key, val], force=True)
    assert qkey == '"1"'
    assert qval == '"10"'


def test_quote_single():
    """Test quote integer value"""
    string = "Long string with spaces"
    [qstring] = u.quote_tags(string)
    assert qstring == '"Long string with spaces"'


def test_dot_dict_setitem():
    """Test DotDict"""
    dic = u.DotDict()
    assert type(dic) == u.DotDict
    dic['id'] = '1'
    dic['path'] = 'test.txt'
    dic['type'] = 'txt'
    dic['view'] = 'text'
    assert getattr(dic, 'id')
    assert getattr(dic, 'path')
    assert getattr(dic, 'type')
    assert getattr(dic, 'view')


def test_dot_dict_setattr():
    """Test DotDict"""
    dic = u.DotDict()
    dic.id = '1'
    dic.path = 'test.txt'
    dic.type = 'txt'
    dic.view = 'text'
    assert getattr(dic, 'id')
    assert getattr(dic, 'path')
    assert getattr(dic, 'type')
    assert getattr(dic, 'view')


def test_dot_dict_of_dict_setitem():
    """Test DotDict"""
    dic = u.DotDict()
    dic['id'] = '1'
    dic['info'] = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    assert getattr(dic, 'id')
    assert getattr(dic, 'info')
    assert type(dic.info) == u.DotDict
    assert getattr(dic.info, 'path')
    assert getattr(dic.info, 'type')
    assert getattr(dic.info, 'view')


def test_dot_dict_of_dict_setattr():
    """Test DotDict"""
    dic = u.DotDict()
    dic.id = '1'
    dic.info = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    assert getattr(dic, 'id')
    assert getattr(dic, 'info')
    assert type(dic.info) == u.DotDict
    assert getattr(dic.info, 'path')
    assert getattr(dic.info, 'type')
    assert getattr(dic.info, 'view')


def test_dot_dict_init():
    """Test DotDict"""
    dic = u.DotDict(id="1", path="test.txt", type="txt", view="text")
    assert type(dic) == u.DotDict
    assert getattr(dic, 'id')
    assert getattr(dic, 'path')
    assert getattr(dic, 'type')
    assert getattr(dic, 'view')


def test_dot_dict_of_dict_init():
    """Test DotDict"""
    dic = u.DotDict(id="1", info={'path': 'test.txt',
                                  'type': 'txt',
                                  'view': 'text'})
    assert type(dic) == u.DotDict
    assert getattr(dic, 'id')
    assert getattr(dic, 'info')
    assert type(dic.info) == u.DotDict
    assert getattr(dic.info, 'path')
    assert getattr(dic.info, 'type')
    assert getattr(dic.info, 'view')


def test_lookup_dict_init():
    dic = u.DotDict(id="1", path="test.txt", type="txt", view="text")
    assert type(dic) == u.DotDict
    assert getattr(dic, 'id')
    assert getattr(dic, 'path')
    assert getattr(dic, 'type')
    assert getattr(dic, 'view')
    assert hasattr(dic, 'lookup')
    assert callable(getattr(dic, 'lookup'))
    assert dic.lookup('1') == ['id']


def test_lookup_dict_of_dict():
    """Test DotDict"""
    dic = u.DotDict(id="1", info={'path': 'test.txt',
                                     'type': 'txt',
                                     'view': 'text'})
    assert type(dic) == u.DotDict
    assert getattr(dic, 'id')
    assert getattr(dic, 'info')
    assert hasattr(dic, 'lookup')
    assert callable(getattr(dic, 'lookup'))
    assert type(dic.info) == u.DotDict
    assert getattr(dic.info, 'path')
    assert getattr(dic.info, 'type')
    assert getattr(dic.info, 'view')
    assert dic.lookup('txt') == ['info.type']


def test_deepcopy():
    """Test DotDict"""
    dic = u.DotDict(id="1", info={'path': 'test.txt',
                                     'type': 'txt',
                                     'view': 'text'})
    assert type(dic) == u.DotDict
    assert getattr(dic, 'id')
    assert getattr(dic, 'info')
    assert hasattr(dic, 'lookup')
    assert callable(getattr(dic, 'lookup'))
    assert type(dic.info) == u.DotDict
    assert getattr(dic.info, 'path')
    assert getattr(dic.info, 'type')
    assert getattr(dic.info, 'view')
    cp = deepcopy(dic)
    assert type(cp) == u.DotDict
    assert getattr(cp, 'id')
    assert getattr(cp, 'info')
    assert hasattr(cp, 'lookup')
    assert callable(getattr(cp, 'lookup'))
    assert type(cp.info) == u.DotDict
    assert getattr(cp.info, 'path')
    assert getattr(cp.info, 'type')
    assert getattr(cp.info, 'view')
