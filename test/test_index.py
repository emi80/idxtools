"""Unit test for the Index class"""
import pytest
import indexfile
from indexfile.index import Index


def test_create_empty():
    """Create empty index"""
    i = Index()
    assert i is not None
    assert i.format == indexfile.default_format
    assert len(i) == 0


def test_create_empty_w_format():
    """Create empty index with custom format"""
    form = {
        "id": "labExpId",
        "colsep": "\t",
        "fileinfo": [
            "path",
            "size",
            "md5"
        ],
        "kw_sep": " ",
        "sep": "=",
        "trail": ";"
    }
    i = Index(format=form)
    assert i is not None
    assert i.format != indexfile.default_format
    assert len(i) == 0


def test_set_format_string():
    """Test set format with JSON string"""
    form = '''{
        "id": "labExpId",
        "colsep": "\\t",
        "fileinfo": [
            "path",
            "size",
            "md5"
        ],
        "kw_sep": " ",
        "sep": "=",
        "trail": ";"
    }'''
    i = Index()
    assert i is not None
    assert i.format == indexfile.default_format
    i.set_format(form)
    assert i.format
    assert i.format != indexfile.default_format


def test_set_format_file():
    """Test set format with file path"""
    i = Index()
    assert i is not None
    assert i.format == indexfile.default_format
    i.set_format('test/data/format.json')
    assert i.format
    assert i.format != indexfile.default_format


def test_open_empty():
    """Open empty index"""
    i = Index()
    assert i is not None
    # Disable warning about:
    # - missing pytest.raises
    # - statement with no effect
    # pylint: disable=E1101,W0104
    with pytest.raises(AttributeError):
        i.open()
    # pylint: enable=E1101,W0104


def test_load_existing():
    """Load existing index"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    assert len(i) == 36


def test_open_string():
    """Test open with string parameter"""
    i = Index()
    assert i is not None
    i.set_format('test/data/format.json')
    i.open('test/data/index.txt')
    assert len(i) == 36


def test_open_file():
    """Test open with file parameter"""
    i = Index()
    assert i is not None
    i.set_format('test/data/format.json')
    f = open('test/data/index.txt','r')
    i.open(f)
    f.close()
    assert len(i) == 36


def test_export():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export()
    assert len(exp) == 36


def test_export_no_map():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    i.export(map=None)


def test_export_no_map_tab_tags():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    i.export(map=None, type='tab', tags=['id', 'path'])


def test_export_no_map_tab_all_tags():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    i.export(map=None, type='tab')


def test_replicates():
    """Test merged datasets"""
    i = Index('test/data/index.txt')
    i.set_format('test/data/format.json')
    i.open()
    reps = i.find_replicates(id="EWP.1,EWP.2")
    dataset = reps[0]
    others = reps[1:]
    merged = dataset.merge(others)
    for key in merged.get_meta_tags():
        vals = [getattr(d, key) for d in reps]
        if len(set(vals)) > 1:
            if key == 'id':
                vals = ','.join(vals)
            assert getattr(merged, key) == vals
        else:
            assert getattr(merged, key) == vals[0]


def test_replicates_w_metadata():
    """Test merged datasets with metadata"""
    i = Index('test/data/index.txt')
    i.set_format('test/data/format.json')
    i.open()
    i.insert(id='aWL3.1,aWL3.2',
             path='test/data/format.json',
             type='json',
             view='json')
    i.select(id='aWL3.1,aWL3.2')
    i.remove(path='test/data/format.json', clear=True)
