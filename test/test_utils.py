"""Test utility methods"""

from indexfile import utils as u


def test_to_tags():
    """Convert dictionary to indexfile string"""
    info = {'id': '1', 'path': 'test.txt', 'view': 'text', 'type': 'txt'}
    # Disable warning about * magic
    # pylint: disable=W0142
    out = u.to_tags(**info)
    # pylint: enable=W0142
    assert out == "id=1; path=test.txt; type=txt; view=text;"


def test_quote_key():
    """Test quote key"""
    key = "Long key with space"
    val = "1"
    qkey, qval = u.quote_kw(key, val, 'key')
    assert qkey == '"Long key with space"'
    assert qval == "1"


def test_quote_val():
    """Test quote value"""
    key = "1"
    val = "Long value with space"
    qkey, qval = u.quote_kw(key, val, 'value')
    assert qkey == "1"
    assert qval == '"Long value with space"'


def test_quote_both():
    """Test quote both"""
    key = "Long key with space"
    val = "Long value with space"
    qkey, qval = u.quote_kw(key, val, 'both')
    assert qkey == '"Long key with space"'
    assert qval == '"Long value with space"'


def test_quote_auto():
    """Test auto quote"""
    key = "Long key with space"
    val = "Long value with space"
    qkey, qval = u.quote_kw(key, val, 'key')
    assert qkey == '"Long key with space"'
    assert qval == '"Long value with space"'
    qkey, qval = u.quote_kw(key, val, 'val')
    assert qkey == '"Long key with space"'
    assert qval == '"Long value with space"'


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
