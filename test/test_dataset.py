"""Unit tests for the Dataset class"""
import pytest
from indexfile.dataset import Dataset


def test_create_empty_dataset():
    """Create empty dataset"""
    dataset = Dataset()
    with pytest.raises(AttributeError):
        dataset.id


def test_create_dataset():
    """Create dataset with string values only"""
    mdata = {'id': '1', 'sex': 'M', 'age': '65'}
    dataset = Dataset(**mdata)
    assert dataset.id == '1'
    assert dataset.sex == 'M'
    assert dataset.age == '65'


def test_create_dataset_w_numbers():
    """Create dataset with string and numeric values"""
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    assert dataset.id == '1'
    assert dataset.sex == 'M'
    assert dataset.age == 65


def test_create_dataset_w_path():
    """Create dataset with file path"""
    mdata = {'id': '1', 'path': 'test.txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    assert not hasattr(dataset, 'path')
    assert not hasattr(dataset, 'type')
    assert len(dataset) == 1
    assert dataset._files is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'text'
    assert dataset.txt == [('test.txt', {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view':'text'})]
    assert dataset.text == [('test.txt', {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view':'text'})]


def test_create_dataset_w_path_type():
    """Create dataset with file path"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    assert not hasattr(dataset, 'path')
    assert not hasattr(dataset, 'type')
    assert len(dataset) == 1
    assert dataset._files is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'text'
    assert dataset.txt == [('test.txt', {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view':'text'})]
    assert dataset.text == [('test.txt', {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view':'text'})]


def test_create_dataset_w_na():
    """Create dataset with file path"""
    mdata = {'id': '1', 'age': 65, 'sex': ''}
    dataset = Dataset(**mdata)
    assert len(dataset) == 0
    assert dataset.id == '1'
    assert dataset.age == 65
    assert dataset.sex == 'NA'


def test_repr():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    assert repr(dataset) == '(Dataset 1)'


def test_str():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    assert str(dataset) == "[{'age': 65, 'id': '1', 'sex': 'M'}]"


def test_add_file():
    """Add file to existing dataset"""
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    fdata = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.add_file(**fdata)
    assert len(dataset) == 1
    assert dataset is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'text'
    assert dataset.txt == [('test.txt', {'id': '1', 'sex': 'M', 'age': 65, 'path': 'test.txt', 'type': 'txt', 'view':'text'})]


def test_add_file_exists():
    """Add file to existing dataset"""
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    fdata = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    with pytest.raises(IOError):
        dataset.add_file(check_exists=True, **fdata)


def test_add_file_update():
    """Add file to existing dataset"""
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    fdata = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    newfdata = {'path': 'test.txt', 'type': 'txt', 'view': 'Text'}
    dataset = Dataset(**mdata)
    dataset.add_file(**fdata)
    dataset.add_file(**newfdata)
    assert dataset['test.txt'].get('view') == 'text'
    dataset.add_file(update=True, **newfdata)
    assert len(dataset) == 1
    assert dataset._files is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'Text'


def test_add_file_update_type():
    """Add file to existing dataset"""
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    fdata = {'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    newfdata = {'path': 'test.txt', 'type': 'text', 'view': 'Text'}
    dataset = Dataset(**mdata)
    dataset.add_file(**fdata)
    dataset.add_file(**newfdata)
    assert dataset['test.txt'].get('view') == 'text'
    assert dataset['test.txt'].get('type') == 'txt'
    dataset.add_file(update=True, **newfdata)
    assert len(dataset) == 1
    assert dataset._files is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'text'
    assert dataset['test.txt'].get('view') == 'Text'


def test_add_file_no_path():
    """Add file with no path"""
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    fdata = {'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.add_file(**fdata)
    assert len(dataset) == 0


def test_add_file_missing_values():
    """Add file with no path"""
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    fdata = {'path': 'test.txt', 'type': 'txt', 'view': ''}
    dataset = Dataset(**mdata)
    dataset.add_file(**fdata)
    assert len(dataset) == 1
    assert dataset['test.txt'].get('view') == 'NA'


def test_multiple_files():
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.add_file(path='test1.txt', type='txt', view='text')
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    dataset.add_file(path='test1.jpg', type='jpg', view='jpeg')
    assert len(dataset) == 4


def test_iter():
    """Iterates over all files in dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.add_file(path='test1.txt', type='txt', view='text')
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    dataset.add_file(path='test1.jpg', type='jpg', view='jpeg')
    i = 0
    for path, mdata in dataset:
        assert path
        assert mdata
        i += 1
    assert i == 4


def test_rm_file():
    """Remove file from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.add_file(path='test1.txt', type='txt', view='text')
    dataset.rm_file(path='test.txt')
    assert len(dataset) == 1
    with pytest.raises(AttributeError):
        dataset['test.txt']

def test_rm_last_file_for_a_type():
    """Remove file from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    dataset.rm_file(path='test.txt')
    with pytest.raises(AttributeError):
        dataset.txt
    assert len(dataset) == 1


def test_rm_last_file():
    """Remove file from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.rm_file(path='test.txt')
    with pytest.raises(AttributeError):
        dataset.txt
    assert len(dataset) == 0


def test_rm_file_type():
    """Remove file from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    dataset.add_file(path='test1.txt', type='txt', view='text')
    assert dataset._files
    assert len(dataset) == 2
    dataset.rm_file(type='txt')
    with pytest.raises(AttributeError):
        dataset['test1.txt']


def test_rm_file_no_path_no_type():
    """Remove file from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    assert len(dataset) == 1
    dataset.rm_file(id='1')
    assert len(dataset) == 1


def test_rm_file_not_existing_file():
    """Remove file from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    assert len(dataset) == 1
    dataset.rm_file(path='test.pdf')
    assert len(dataset) == 1


def test_rm_file_native():
    """Remove file from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
    assert len(dataset) == 1
    del dataset.txt
    assert len(dataset) == 0
    del dataset.txt
    assert len(dataset) == 0
    dataset.add_file(path='test.pdf', type='pdf', view='PDF')
    assert len(dataset) == 1
    assert dataset.pdf == [('test.pdf',{'id': '1', 'path': 'test.pdf', 'type':'pdf', 'view':'PDF'})]
    assert dataset['test.pdf'] == {'path': 'test.pdf', 'type':'pdf', 'view':'PDF'}
    del dataset['test.pdf']
    assert len(dataset) == 0


def test_export_all():
    """Export files from dataset"""
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
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
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
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
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
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
    mdata = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    dataset = Dataset(**mdata)
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


def test_merge():
    """Merge metadata from two or more datasets"""
    info1 = {'id': '1', 'sex': 'M', 'age': 65, 'desc': 'First test dataset'}
    info2 = {'id': '2', 'sex': 'F', 'age': 61, 'desc': 'Second test dataset'}
    dataset1 = Dataset(**info1)
    dataset2 = Dataset(**info2)
    merged = dataset1.merge(dataset2)
    assert merged is not None
    assert merged.id == '1,2'
    assert merged.sex == ['M', 'F']
    assert merged.age == [65, 61]
    assert merged.desc == ['First test dataset', 'Second test dataset']


def test_dataset_clone():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    dataset.add_file(id='1', path='test.txt', type='txt')
    dataset.add_file(id='1', path='test.bam', type='bam')
    assert len(dataset) == 2
    clone = dataset.clone()
    assert id(dataset) != id(clone)
    assert type(dataset) == type(clone)
    assert dataset._metadata == clone._metadata
    assert dataset._files == clone._files
    assert hasattr(clone, "clone")
    assert hasattr(clone, "add_file")
    assert hasattr(clone, "rm_file")
    assert hasattr(clone, "export")
    assert hasattr(clone, "merge")
    assert hasattr(clone, "get")


def test_dataset_has():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    result = {'age': 65} in dataset
    assert result is True
    dataset.add_file(id='1', path='test.txt', type='txt')
    result = {'type': 'txt'} in dataset
    assert result is True


def test_dataset_contains():
    # metadata
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    assert {'age': 65} in dataset
    assert {'sex': 'M'} in dataset
    # files
    dataset.add_file(id='1', path='test.txt', type='txt')
    dataset.add_file(id='1', path='test.gff', type='gff')
    assert {'id': '1'} in dataset
    assert {'id': 1} not in dataset
    assert {'id': '2'} not in dataset
    assert {'type': 'txt'} in dataset
    assert {'path': 'test'} in dataset
    assert {'path': 'test', 'exact': True} not in dataset
    assert {'type': 'pdf'} not in dataset
    assert {'age': 65, 'type': 'gff'} in dataset
    assert {'age': 65, 'type': 'gff', 'match_all': True} not in dataset
    assert {'gender': 'M'} not in dataset
    assert {'size': 1000} not in dataset
    assert {'md5': '098f6bcd4621d373cade4e832627b4f6'} not in dataset


def test_dataset_dice_exact():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    dataset.add_file(id='1', path='test.txt', type='txt')
    txt = dataset.dice(type='txt', exact=True)
    assert txt
    assert type(txt) == Dataset
    assert len(txt) == 1
    dataset.add_file(id='1', path='test1.txt', type='txt')
    txt = dataset.dice(type='txt')
    assert len(txt) == 2
    txt = dataset.dice(type='t', exact=True)
    assert isinstance(txt, Dataset)
    assert len(txt) == 0

def test_dataset_dice_regex_simple():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    dataset.add_file(id='1', path='test.txt', type='txt')
    txt = dataset.dice(type='txt')
    assert txt
    assert type(txt) == Dataset
    assert len(txt) == 1
    dataset.add_file(id='1', path='test1.txt', type='txt')
    txt = dataset.dice(type='t')
    assert len(txt) == 2


def test_dataset_dice_regex():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    dataset.add_file(id='1', path='test.gtf', type='gtf')
    dataset.add_file(id='1', path='test.gff', type='gff')
    txt = dataset.dice(type='g[tf]f')
    assert type(txt) == Dataset
    assert len(txt) == 2


def test_dataset_dice_ops():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    dataset.add_file(id='1', path='test.gtf', type='gtf', size=100)
    dataset.add_file(id='1', path='test.gff', type='gff', size=50)
    txt = dataset.dice(size='>50')
    assert type(txt) == Dataset
    assert len(txt) == 1
    assert txt.get('test.gff') is None
    assert txt.get('test.gtf') is not None


def test_dataset_dice_ops():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    dataset.add_file(id='1', path='test.gtf', type='gtf', size=100)
    dataset.add_file(id='1', path='test.gff', type='gff', size=50)
    with pytest.raises(SyntaxError):
        txt = dataset.dice(size='!50')


def test_dataset_callbacks():
    mdata = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**mdata)
    def age_cb(d):
        if d.age > 50:
            return "old"
        return young
    dataset.myAge = age_cb
    assert dataset.myAge == "old"
    assert dataset['myAge'] == "old"
    assert dataset.get('myAge') == "old"
