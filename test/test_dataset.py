"""Unit tests for the Dataset class"""
import pytest
from indexfile.config import config
from indexfile.dataset import Dataset

config.fileinfo.add('view')

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
    assert dataset._files is not None
    assert dataset.get('test.txt') is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'text'


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
    assert dataset._files is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'text'


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


def test_repr():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert repr(dataset) == '(Dataset)'

def test_str():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert str(dataset) == 'age=65; id=1; sex=M;'


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
    assert dataset is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'text'


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
    assert dataset['test.txt'].get('view') == 'text'
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset.add_file(update=True, **newfileinfo)
    # pylint: enable=W0142
    assert len(dataset) == 1
    assert dataset._files is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'txt'
    assert dataset['test.txt'].get('view') == 'Text'


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
    assert dataset['test.txt'].get('view') == 'text'
    assert dataset['test.txt'].get('type') == 'txt'
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset.add_file(update=True, **newfileinfo)
    # pylint: enable=W0142
    assert len(dataset) == 1
    assert dataset._files is not None
    assert dataset['test.txt'] is not None
    assert dataset['test.txt'].get('type') == 'text'
    assert dataset['test.txt'].get('view') == 'Text'


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
    assert len(dataset) == 0


def test_add_file_missing_values():
    """Add file with no path"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    fileinfo = {'path': 'test.txt', 'type': 'txt', 'view': ''}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset.add_file(**fileinfo)
    # pylint: enable=W0142
    assert len(dataset) == 1
    assert dataset['test.txt'].get('view') == 'NA'


def test_multiple_files():
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    dataset.add_file(path='test1.txt', type='txt', view='text')
    dataset.add_file(path='test.jpg', type='jpg', view='jpeg')
    dataset.add_file(path='test1.jpg', type='jpg', view='jpeg')
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
    assert len(dataset) == 1
    assert dataset['test.txt'] is None


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
    assert dataset._files
    assert len(dataset) == 2
    dataset.rm_file(type='txt')
    # Disable warning about:
    # - missing pytest.raises.
    # - statement with no effect
    # pylint: disable=E1101,W0104
    with pytest.raises(AttributeError):
        dataset.txt
    # pylint: enable=E1101,W0104


def test_rm_file_no_path_no_type():
    """Remove file from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert len(dataset) == 1
    dataset.rm_file(id='1')
    assert len(dataset) == 1


def test_rm_file_not_existing_file():
    """Remove file from dataset"""
    info = {'id': '1', 'path': 'test.txt', 'type': 'txt', 'view': 'text'}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    assert len(dataset) == 1
    dataset.rm_file(path='test.pdf')
    assert len(dataset) == 1


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


def test_get_tags_only_one():
    """Concatenate metadata tags from dataset with exclusion list"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = Dataset(**info)
    # pylint: enable=W0142
    string = dataset.get_tags(tags='id')
    assert string == "id=1;"


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


def test_dataset_clone():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    dataset.add_file(id='1', path='test.txt', type='txt')
    dataset.add_file(id='1', path='test.bam', type='bam')
    assert len(dataset) == 2
    clone = dataset.clone()
    assert id(dataset) != id(clone)
    assert type(dataset) == type(clone)
    assert dataset._metadata == clone._metadata
    assert dataset._files == clone._files
    assert dataset._attributes == clone._attributes
    assert hasattr(clone, "clone")
    assert hasattr(clone, "add_file")
    assert hasattr(clone, "rm_file")
    assert hasattr(clone, "export")
    assert hasattr(clone, "get_meta_tags")
    assert hasattr(clone, "get_meta_items")
    assert hasattr(clone, "get_tags")
    assert hasattr(clone, "merge")
    assert hasattr(clone, "get")


def test_dataset_has():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    result = {'age': 65} in dataset
    assert result is True
    dataset.add_file(id='1', path='test.txt', type='txt')
    result = {'type': 'txt'} in dataset
    assert result is True


def test_dataset_multi_has():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    result = {'age': 65} in dataset
    assert result is True
    dataset.add_file(id='1', path='test.txt', type='txt')
    dataset.add_file(id='1', path='test.gff', type='gff')
    result = {'type': 'txt'} in dataset
    assert result is True


def test_dataset_has_files():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    dataset.add_file(id='1', path='test.txt', type='txt')
    result = {'type': 'txt'} in dataset
    assert dataset._files


def test_dataset_dice_exact():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    dataset.add_file(id='1', path='test.txt', type='txt')
    txt = dataset.dice(type='txt', exact=True)
    assert txt
    assert type(txt) == Dataset
    assert len(txt) == 1
    dataset.add_file(id='1', path='test1.txt', type='txt')
    txt = dataset.dice(type='txt')
    assert len(txt) == 2
    txt = dataset.dice(type='t', exact=True)
    assert txt is None

def test_dataset_dice_regex_simple():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    dataset.add_file(id='1', path='test.txt', type='txt')
    txt = dataset.dice(type='txt')
    assert txt
    assert type(txt) == Dataset
    assert len(txt) == 1
    dataset.add_file(id='1', path='test1.txt', type='txt')
    txt = dataset.dice(type='t')
    assert len(txt) == 2


def test_dataset_dice_regex():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    dataset.add_file(id='1', path='test.gtf', type='gtf')
    dataset.add_file(id='1', path='test.gff', type='gff')
    txt = dataset.dice(type='g[tf]f')
    assert type(txt) == Dataset
    assert len(txt) == 2


def test_dataset_dice_ops():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    dataset.add_file(id='1', path='test.gtf', type='gtf', size=100)
    dataset.add_file(id='1', path='test.gff', type='gff', size=50)
    txt = dataset.dice(size='>50')
    assert type(txt) == Dataset
    assert len(txt) == 1
    assert txt.get('test.gff') is None
    assert txt.get('test.gtf') is not None


def test_dataset_dice_ops():
    info = {'id': '1', 'sex': 'M', 'age': 65}
    dataset = Dataset(**info)
    dataset.add_file(id='1', path='test.gtf', type='gtf', size=100)
    dataset.add_file(id='1', path='test.gff', type='gff', size=50)
    with pytest.raises(SyntaxError):
        txt = dataset.dice(size='!50')


class MyDataset(Dataset):
    """My test dataset"""
    def __init__(self, **kwargs):
        super(MyDataset, self).__init__(**kwargs)

        self._init_attributes()

    def _init_attributes(self):
        """Initialize attributes"""
        self._attributes['test'] = (lambda x: "This is a dataset"
                                    if type(x) == MyDataset else None)


def test_attributes():
    """Test attribute creations and accession"""
    info = {'id': '1', 'sex': 'M', 'age': 65}
    # Disable warning about * magic
    # pylint: disable=W0142
    dataset = MyDataset(**info)
    # pylint: enable=W0142
    assert dataset.test == "This is a dataset"
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
