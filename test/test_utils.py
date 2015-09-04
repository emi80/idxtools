"""Test utility methods"""

import pytest
from copy import deepcopy
from indexfile import utils as u


def test_quote_key():
    """Test quote key"""
    key = "Long key with space"
    val = "1"
    qkey, qval = u.quote([key, val])
    assert qkey == '"Long key with space"'
    assert qval == "1"


def test_quote_val():
    """Test quote value"""
    key = "1"
    val = "Long value with space"
    qkey, qval = u.quote([key, val])
    assert qkey == "1"
    assert qval == '"Long value with space"'


def test_quote_int():
    """Test quote integer value"""
    key = 1
    val = 10
    qkey, qval = u.quote([key, val], force=True)
    assert qkey == '"1"'
    assert qval == '"10"'


def test_quote_single():
    """Test quote integer value"""
    string = "Long string with spaces"
    [qstring] = u.quote(string)
    assert qstring == '"Long string with spaces"'


def test_match():
    assert u.match(65, 65)
    assert u.match(65, [65])
    assert not u.match(65, ['65'])
    # exact
    assert u.match("a", "a", exact=True)
    assert u.match(1, 1, exact=True)
    assert not u.match(1, "1", exact=True)
    # regular expressions
    assert u.match(r"a", "atom")
    assert u.match(r"ca[rt]", "cat")
    assert u.match(r".+ar$", "car")
    assert u.match(r"[^3]", "4")
    # operators
    assert u.match(r">2", 20)
    assert u.match(r">=2", 2)
    assert u.match(r"!=3", 4)
    assert u.match(r"!=3", "4")
    assert u.match(r">3", "5")
    with pytest.raises(SyntaxError):
      assert u.match(r"!1", "2")
    assert not u.match(r">3", "d")
    # list
    assert u.match("a", ["atom","cat","dog"])
    assert u.match("ca[rt]", ["cat", "cart"])
    assert u.match(">2", [1,3,2,20])
    # list all_true
    assert not u.match(">2", [1,3,2,20], match_all=True)
    assert not u.match("a", ["atom","cat","dog"], match_all=True)


def test_get_file_type():
    assert u.get_file_type('test.txt') == 'txt'
    assert u.get_file_type('test.txt.gz') == 'txt'
    assert u.get_file_type('test') == ''


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


def test_DotDict_update():
    """Test DotDict update method"""
    dic = u.DotDict(id="1", info={'path': 'test.txt',
                                     'type': 'txt',
                                     'view': 'text'})
    assert dic.info.view == 'text'
    dic.update(info={'view':'Text'}, stat=dict(size=10))
    assert dic.id == '1'
    assert type(dic.info) == u.DotDict
    assert dic.info.view == 'Text'
    assert dic.stat
    assert type(dic.stat) == u.DotDict
    assert dic.stat.size == 10


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
