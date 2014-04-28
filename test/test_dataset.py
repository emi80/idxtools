"""Unit tests for the Dataset class"""
import pytest
from indexfile.index import Dataset


def test_create_empty_dataset():
    """Create empty dataset"""
    dataset = Dataset()
    # Disable warning about:
    # - missing pytest.raises
    # - statement with no effect
    # pylint: disable=E1101,W0104
    with pytest.raises(AttributeError):
        dataset.id
    # pylint: enable=E1101,W0104


def test_create_dataset():
    """Create dataset with string values only"""
    info = {'id': '1', 'sex': 'M', 'age': '65'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert dataset.id == '1'
    assert dataset.sex == 'M'
    assert dataset.age == '65'


def test_create_dataset_w_numbers():
    """Create dataset with string and numeric values"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert dataset.id == '1'
    assert dataset.sex == 'M'
    assert dataset.age == 65


def test_create_dataset_w_path():
    """Create dataset with file path"""
    info = {'id': '1', 'path': 'test.txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert not hasattr(dataset, 'path')
    assert not hasattr(dataset, 'type')
    assert len(dataset) == 1
    assert dataset.txt is not None
    assert len(dataset.txt) == 1
    assert dataset.txt.get('test.txt') is not None
    assert dataset.txt.get('test.txt').get('type') == 'txt'
    assert dataset.txt.get('test.txt').get('view') == 'text'


def test_create_dataset_w_path_type():
    """Create dataset with file path"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert not hasattr(dataset, 'path')
    assert not hasattr(dataset, 'type')
    assert len(dataset) == 1
    assert dataset.txt is not None
    assert len(dataset.txt) == 1
    assert dataset.txt.get('test.txt') is not None
    assert dataset.txt.get('test.txt').get('type') == 'txt'
    assert dataset.txt.get('test.txt').get('view') == 'text'


def test_create_dataset_w_na():
    """Create dataset with file path"""
    info = {'id': '1', 'age': 65, 'sex': ''}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert len(dataset) == 0
    assert dataset.id == '1'
    assert dataset.age == 65
    assert dataset.sex == 'NA'


def test_add_file():
    """Add file to existing dataset"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    fileinfo = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset.add_file(**fileinfo)
    # pylint: enable=W0142
    assert len(dataset) == 1
    assert dataset.txt is not None
    assert len(dataset.txt) == 1
    assert dataset.txt.get('test.txt') is not None
    assert dataset.txt.get('test.txt').get('type') == 'txt'
    assert dataset.txt.get('test.txt').get('view') == 'text'


def test_add_file_update():
    """Add file to existing dataset"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    fileinfo = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    newfileinfo = {'path': 'test.txt', 'type': 'txt', 'view': 'Text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    dataset.add_file(**fileinfo)
    dataset.add_file(**newfileinfo)
    # pylint: enable=W0142
    assert dataset.txt.get('test.txt').get('view') == 'text'
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset.add_file(update=True, **newfileinfo)
    # pylint: enable=W0142
    assert len(dataset) == 1
    assert dataset.txt is not None
    assert len(dataset.txt) == 1
    assert dataset.txt.get('test.txt') is not None
    assert dataset.txt.get('test.txt').get('type') == 'txt'
    assert dataset.txt.get('test.txt').get('view') == 'Text'


def test_add_file_update_type():
    """Add file to existing dataset"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    fileinfo = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    newfileinfo = {'path': 'test.txt', 'type': 'text', 'view': 'Text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    dataset.add_file(**fileinfo)
    dataset.add_file(**newfileinfo)
    # pylint: enable=W0142
    assert dataset.txt.get('test.txt').get('view') == 'text'
    assert not hasattr(dataset,'text')
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset.add_file(update=True, **newfileinfo)
    # pylint: enable=W0142
    assert len(dataset) == 1
    assert not hasattr(dataset,'txt')
    assert dataset.text is not None
    assert len(dataset.text) == 1
    assert dataset.text.get('test.txt') is not None
    assert dataset.text.get('test.txt').get('type') == 'text'
    assert dataset.text.get('test.txt').get('view') == 'Text'


def test_add_file_no_path():
    """Add file with no path"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    fileinfo = {'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset.add_file(**fileinfo)
    # pylint: enable=W0142
    print dataset._files
    assert len(dataset) == 0
    assert not hasattr(dataset, 'txt')


def test_multiple_files():
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test1.txt', type='txt', view='text')
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    dataset.add_file(path='test1.jpg', type='jpg', view='jpeg')
    assert dataset.txt
    assert dataset.jpg
    assert len(dataset.txt) == 2
    assert len(dataset.jpg) == 2
    assert len(dataset) == 4


def test_iter():
    """Iterates over all files in dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test1.txt', type='txt', view='text')
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    dataset.add_file(path='test1.jpg', type='jpg', view='jpeg')
    i = 0
    for path, info in dataset:
        assert path
        assert info
        i += 1
    assert i == 4


def test_rm_file():
    """Remove file from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test1.txt', type='txt', view='text')
    dataset.rm_file(path='test.txt')
    assert dataset.txt
    assert len(dataset.txt) == 1
    assert dataset.txt.get('test.txt') is None


def test_rm_last_file_for_a_type():
    """Remove file from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    dataset.rm_file(path='test.txt')
    # Disable warning about:
    # - missing pytest.raises.
    # - statement with no effect
    # pylint: disable=E1101,W0104
    with pytest.raises(AttributeError):
        dataset.txt
    # pylint: enable=E1101,W0104
    assert len(dataset) == 1


def test_rm_last_file():
    """Remove file from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
        # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.rm_file(path='test.txt')
    # Disable warning about:
    # - missing pytest.raises.
    # - statement with no effect
    # pylint: disable=E1101,W0104
    with pytest.raises(AttributeError):
        dataset.txt
    # pylint: enable=E1101,W0104
    assert len(dataset) == 0


def test_rm_file_type():
    """Remove file from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test1.txt', type='txt', view='text')
    assert dataset.txt
    assert len(dataset.txt) == 2
    dataset.rm_file(type='txt')
    # Disable warning about:
    # - missing pytest.raises.
    # - statement with no effect
    # pylint: disable=E1101,W0104
    with pytest.raises(AttributeError):
        dataset.txt
    # pylint: enable=E1101,W0104


def test_export_all():
    """Export files from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    exp = dataset.export()
    assert exp
    assert len(exp) == 2
    for dic in exp:
        assert len(dic) == 4
        assert dic.get('path') is not None
        assert dic.get('type') is not None
        assert dic.get('id') is not None
        assert dic.get('view') is not None


def test_export_type():
    """Export files from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    exp = dataset.export(types='jpg')
    assert exp
    assert len(exp) == 1
    for dic in exp:
        assert len(dic) == 4
        assert dic.get('path') == 'test.jpg'
        assert dic.get('type') == 'jpg'
        assert dic.get('id') == '1'
        assert dic.get('view') == 'jpeg'


def test_export_tag():
    """Export files from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    exp = dataset.export(tags=['path', 'view'])
    assert exp
    assert len(exp) == 2
    for dic in exp:
        assert len(dic) == 2
        assert dic.get('path') is not None
        assert dic.get('view') is not None
        assert dic.get('id') is None
        assert dic.get('type') is None


def test_export_one_tag():
    """Export files from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    exp = dataset.export(tags='path')
    assert exp
    assert len(exp) == 2
    for dic in exp:
        assert len(dic) == 1
        assert dic.get('path') is not None
        assert dic.get('view') is None
        assert dic.get('id') is None
        assert dic.get('type') is None


def test_get_tags_all():
    """Concatenate all metadata tags from dataset"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    string = dataset.get_tags()
    assert string == "age=65; id=1; sex=M;"


def test_get_tags_all_w_quotes():
    """Concatenate all metadata tags from dataset"""
    info = {'id': '1', 'sex': 'M', 'age': 65, 'desc': 'A test dataset'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    string = dataset.get_tags()
    assert string == "age=65; desc=\"A test dataset\"; id=1; sex=M;"


def test_get_tags_exclude():
    """Concatenate metadata tags from dataset with exclusion list"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    string = dataset.get_tags(exclude='sex')
    assert string == "age=65; id=1;"


def test_get_tags_include():
    """Concatenate metadata tags from dataset with exclusion list"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    string = dataset.get_tags(tags=['id', 'sex'])
    assert string == "id=1; sex=M;"


def test_merge():
    """Merge metadata from two or more datasets"""
    info1 = {'id': '1', 'sex': 'M', 'age': 65, 'desc': 'First test dataset'}
    info2 = {'id': '2', 'sex': 'F', 'age': 61, 'desc': 'Second test dataset'}
     # Disable warning about * magic
    # pylint: disable=W0142
    dataset1 = Dataset(**info1)
    dataset2 = Dataset(**info2)
    # pylint: enable=W0142
    merged = dataset1.merge(dataset2)
    assert merged is not None
    assert merged.id == '1,2'
    assert merged.sex == ['M', 'F']
    assert merged.age == [65, 61]
    assert merged.desc == ['First test dataset', 'Second test dataset']


def test_get_tags_on_merged():
    """Merge metadata from two or more datasets"""
    info1 = {'id': '1', 'sex': 'M', 'age': 65, 'desc': 'First test dataset'}
    info2 = {'id': '2', 'sex': 'F', 'age': 61, 'desc': 'Second test dataset'}
     # Disable warning about * magic
    # pylint: disable=W0142
    dataset1 = Dataset(**info1)
    dataset2 = Dataset(**info2)
    # pylint: enable=W0142
    merged = dataset1.merge(dataset2)
    string = merged.get_tags()
    assert string == '''age=65,61; desc="First test dataset","Second test dataset"; id=1,2; sex=M,F;'''
