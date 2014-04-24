"""Unit test for the Index class"""
import pytest
from indexfile.index import Index


def test_create_empty():
    """Create empty index"""
    i = Index()
    assert i is not None
    assert len(i) == 0


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
