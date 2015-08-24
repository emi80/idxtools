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


def test_set_format_none():
    """Test set format with no argument"""
    i = Index()
    assert i is not None
    assert i.format == indexfile.default_format
    i.set_format()
    assert i.format
    assert i.format == indexfile.default_format


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


def test_insert():
    """Test insertion into the index"""
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    assert len(i.datasets) == 1
    dataset = i.datasets.get('1')
    assert dataset is not None
    assert len(dataset) == 1
    assert hasattr(dataset, 'id')
    assert hasattr(dataset, 'age')
    assert dataset.id == '1'
    assert dataset.age == 65
    assert dataset.dice('test.txt') is not None
    assert len(dataset['test.txt']) == 1
    assert hasattr(dataset['test.txt'], 'type')
    assert dataset['test.txt'].type == 'txt'


def test_insert_non_default_fileinfo():
    """Test insertion into the index with specified fileinfo"""
    i = Index()
    i.format['fileinfo'] = ['path', 'type', 'date']
    i.insert(id='1', age=65, path='test.txt', type='txt', date='20150304')
    assert len(i.datasets) == 1
    dataset = i.datasets.get('1')
    assert dataset is not None
    assert len(dataset) == 1
    assert hasattr(dataset, 'id')
    assert hasattr(dataset, 'age')
    assert dataset.id == '1'
    assert dataset.age == 65
    assert dataset.dice('test.txt') is not None
    assert len(dataset['test.txt']) == 2
    assert hasattr(dataset['test.txt'], 'type')
    assert hasattr(dataset['test.txt'], 'date')
    assert dataset['test.txt'].type == 'txt'


def test_insert_update():
    """Test insertion into the index"""
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    i.insert(id='1', age=70, path='test.txt', type='text', update=True)
    assert len(i.datasets) == 1
    dataset = i.datasets.get('1')
    assert dataset is not None
    assert len(dataset) == 1
    assert hasattr(dataset, 'id')
    assert hasattr(dataset, 'age')
    assert dataset.id == '1'
    assert dataset.age == 70
    assert len(dataset['test.txt']) == 1
    assert hasattr(dataset['test.txt'], 'type')
    assert dataset['test.txt'].type == 'text'

def test_insert_update_exc():
    """Test insertion into the index adding non-existing keys"""
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    with pytest.raises(AttributeError):
        i.insert(id='1', age=70, path='test.txt', type='text', length=20, update=True)

def test_insert_force_update():
    """Test insertion into the index"""
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    i.insert(id='1', age=70, path='test.txt', type='text', length=20, update=True, addkeys=True)
    assert len(i.datasets) == 1
    dataset = i.datasets.get('1')
    assert dataset is not None
    assert len(dataset) == 1
    assert hasattr(dataset, 'id')
    assert hasattr(dataset, 'age')
    assert dataset.id == '1'
    assert dataset.age == 70
    assert dataset.length == 20
    assert len(dataset['test.txt']) == 1
    assert hasattr(dataset['test.txt'], 'type')
    assert dataset['test.txt'].type == 'text'

def test_add_file_external():
    index = '''.\tage=-; cell=Neutrophils; dataType=RNA-Seq; dateSubmittedFirst=2012-10-17T09:49:23+0200; donorId=C000XW; ethnicity=NA; lab=MPIMG; labExpId=ERR180946; labProtocolId=C000XWB1; libProtocol=I_bc_pelib_858; localization="Primary Cell"; quality=phred; readStrand=MATE2_SENSE; readType=2x76D; rnaExtract=total; seqPlatform=ILLUMINA; seqRun=1; sex=Male; sraSampleAccession=ERS150362; sraStudyAccession=ERP001664; tissue="Cord blood";'''
    i = Index()
    i.set_format('test/data/tsv_format.json')
    i.insert(**Index.parse_line(index, **i.format))
    i.insert(id="ERR180946", path="/users/rg/epalumbo/projects/BluePrint/reads/20130805/data/ERR180946_1.fastq.gz", view="FastqRd1",type="fastq")
    assert i.export(map=None)[0] == '''/users/rg/epalumbo/projects/BluePrint/reads/20130805/data/ERR180946_1.fastq.gz\tage=-; cell=Neutrophils; dataType=RNA-Seq; dateSubmittedFirst=2012-10-17T09:49:23+0200; donorId=C000XW; ethnicity=NA; lab=MPIMG; labExpId=ERR180946; labProtocolId=C000XWB1; libProtocol=I_bc_pelib_858; localization="Primary Cell"; quality=phred; readStrand=MATE2_SENSE; readType=2x76D; rnaExtract=total; seqPlatform=ILLUMINA; seqRun=1; sex=Male; sraSampleAccession=ERS150362; sraStudyAccession=ERP001664; tissue="Cord blood"; type=fastq; view=FastqRd1;'''


def test_lookup_simple_dataset():
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    selected = i.lookup(id='1')
    assert selected.datasets == i.datasets
    dataset = selected.datasets.get('1')
    assert dataset is not None
    assert dataset.id == '1'
    assert dataset.age == 65
    assert len(dataset) == 1


def test_lookup_dataset():
    i = Index()
    i.insert(id='1', age=65, path='test1.txt', type='txt')
    i.insert(id='2', age=63, path='test2.txt', type='txt')
    i.insert(id='3', age=70, path='test3.jpg', type='jpg')
    selected = i.lookup(id='2')
    assert selected.datasets != i.datasets
    dataset = selected.datasets.get('2')
    assert dataset is not None
    assert dataset.id == '2'
    assert dataset.age == 63
    assert len(dataset) == 1


def test_lookup_path():
    i = Index()
    i.insert(id='1', age=65, path='test1.txt', type='txt')
    i.insert(id='2', age=63, path='test2.txt', type='txt')
    i.insert(id='3', age=70, path='test3.jpg', type='jpg')
    selected = i.lookup(path='test3.jpg')
    assert selected.datasets != i.datasets
    dataset = selected.datasets.get('3')
    assert dataset is not None
    assert dataset.id == '3'
    assert dataset.age == 70
    assert len(dataset) == 1


def test_lookup_multiple_terms():
    i = Index()
    i.insert(id='1', age=65, path='test1.txt', type='txt')
    i.insert(id='2', age=63, path='test2.txt', type='txt')
    i.insert(id='3', age=70, path='test3.jpg', type='jpg')
    i.insert(id='4', age=45, path='test4.pdf', type='pdf')
    selected = i.lookup(type='jpg', path='test3.jpg')
    assert selected.datasets != i.datasets
    assert len(selected.datasets) == 1


def test_lookup_multiple():
    i = Index()
    i.insert(id='1', age=65, path='test1.txt', type='txt')
    i.insert(id='2', age=63, path='test2.txt', type='txt')
    i.insert(id='3', age=70, path='test3.jpg', type='jpg')
    i.insert(id='4', age=45, path='test4.pdf', type='pdf')
    selected = i.lookup(type='txt', path='test3.jpg')
    assert selected.datasets != i.datasets
    assert len(selected.datasets) == 0


def test_lookup_multiple_or():
    i = Index()
    i.insert(id='1', age=65, path='test1.txt', type='txt')
    i.insert(id='2', age=63, path='test2.txt', type='txt')
    i.insert(id='3', age=70, path='test3.jpg', type='jpg')
    i.insert(id='4', age=45, path='test4.pdf', type='pdf')
    selected = i.lookup(type='txt', path='test3.jpg', or_query=True)
    assert selected.datasets != i.datasets
    assert len(selected.datasets) == 3


def test_lookup_multiple_or():
    i = Index()
    i.insert(id='1', age=65, path='test1.txt', type='txt')
    i.insert(id='1', age=65, path='test1.gff', type='gff')
    selected = i.lookup(type='txt')
    assert len(selected.datasets.values()[0]) == 1


def test_lookup_no_path():
    i = Index('test/data/index.txt')
    i.set_format('test/data/format.json')
    i.open()
    assert i.datasets.get('WLP.2') is not None
    selected = i.lookup(id='WLP.2')
    assert selected.datasets != i.datasets
    assert len(selected.datasets) == 1
    dataset = selected.datasets.get('WLP.2')
    assert dataset is not None
    dataset.id = 'WLP.2'


def test_lookup_more_types_index_id():
    """Test export"""
    i = Index('test/data/index_gfs.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    result = i.lookup(id='WWP.1')
    assert result.export()[0][0] != '.'


def test_lookup_one_type_index():
    """Test export"""
    i = Index('test/data/index_gtfs.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    result = i.lookup(type='gtf')
    assert result.export()[0][0] != '.'


def test_lookup_more_types_index():
    """Test export"""
    i = Index('test/data/index_one_gfs.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    result = i.lookup(type='gtf')
    assert result != None
    assert result.datasets != {}
    assert result.export()[0][0] != '.'


def test_lookup_full_index():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    result = i.lookup(type='gtf')
    assert result.export()[0][0] != '.'


def test_remove_dataset():
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    i.remove(id='1')
    assert len(i.datasets) == 0


def test_remove_file():
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    i.insert(id='1', path='test1.txt', type='txt')
    assert len(i.datasets) == 1
    dataset = i.datasets.get('1')
    assert len(dataset) == 2
    i.remove(path='test.txt')
    assert len(i.datasets) == 1
    assert len(i.datasets.get('1')) == 1


def test_remove_fileinfo():
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    i.insert(id='1', path='test1.txt', type='txt')
    i.insert(id='1', path='test1.jpg', type='jpeg')
    assert len(i.datasets) == 1
    dataset = i.datasets.get('1')
    assert len(dataset) == 3
    i.remove(type='jpeg')
    print i.datasets.get('1')._files
    assert len(i.datasets) == 1
    assert len(i.datasets.get('1')) == 2


def test_export():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export()
    assert type(exp) == list
    assert len(exp) == 216
    assert 'LIBRARY_ID' in exp[0]


def test_export_oneline():
    """Test export one known line"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export()
    assert exp[0] == '''aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tLIBRARY_ID=aWL3.2; RNA_quantity=100; barcode=AR025; cell=anterior; dataType=rnaSeq; developmental_point=L3; library_Bioanalyser="5.8 ng/uL (30 nM) 08/04/2013"; localization=cell; max_peak=297; n_sequences=37478754; organism=dmel; pool_ID=2; readStrand=MATE1_SENSE; readType=2x75D; replicate=2; rnaExtract=longPolyA; sequence=ACTGAT(A); tissue=wing; type=gtf; view=TranscriptFB554;'''


def test_export_no_map():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None)
    assert len(exp) == 216
    assert 'labExpId' in exp[0]
    assert 'fileinfo' not in exp[0]


def test_export_no_format_no_map():
    """Test export"""
    i = Index()
    #assert i is not None
    i.insert(id="myId", path="test/data/index.txt", type="text", view="TxtFile")
    exp = i.export(map=None, export_type='tab', tags=['id'])
    assert len(exp) == 1
    assert exp[0] == 'myId'


def test_export_no_map_tab_tags_no_miss():
    """Test export without missing values"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['id', 'path'],
                   hide_missing=True)
    assert len(exp) == 200
    assert exp[0] == 'EL3.1\t/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1_5355_ATCACG.minusRaw.bigwig'


def test_export_no_map_tab_repeated_tags():
    """Test export tab output with repeated tags"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['id', 'id', 'path'],
                   hide_missing=True)
    assert len(exp) == 200
    assert exp[0] == 'EL3.1\tEL3.1\t/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1_5355_ATCACG.minusRaw.bigwig'


def test_export_no_map_tab_path_template():
    """Test export tab output with path template"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['path','{dirname}/{id}.{view}.{ext}'],
                   hide_missing=True)
    assert len(exp) == 200
    assert exp[0] == '/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1_5355_ATCACG.minusRaw.bigwig\t/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1.MinusRawSignal.bigwig'


def test_export_oneline_no_map():
    """Test export one known line"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None)
    assert exp[0] == '''aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tadaptor=ACTGAT(A); age=L3; barcode=AR025; cell=anterior; dataType=rnaSeq; labExpId=aWL3.2; libBio="5.8 ng/uL (30 nM) 08/04/2013"; localization=cell; maxPeak=297; nReads=37478754; organism=dmel; poolId=2; readStrand=MATE1_SENSE; readType=2x75D; replicate=2; rnaExtract=longPolyA; rnaQuantity=100; tissue=wing; type=gtf; view=TranscriptFB554;'''


def test_export_ol_no_map_tab_tags():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['id', 'path'])
    print exp[0]
    assert exp[0] == 'aWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_path():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['path'])
    assert exp[0] == 'aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_tags_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['id', 'path'],
                   header=True)
    assert exp[0] == 'labExpId\tpath'
    assert exp[1] == 'aWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_repeated_tags_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['id', 'id', 'path'],
                   header=True)
    assert exp[0] == 'labExpId\tlabExpId\tpath'
    assert exp[1] == 'aWL3.2\taWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_all():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab')
    assert exp[0] == '''ACTGAT(A)\tL3\tAR025\tanterior\trnaSeq\taWL3.2\t"5.8 ng/uL (30 nM) 08/04/2013"\tcell\t297\t37478754\tdmel\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\t2\tMATE1_SENSE\t2x75D\t2\tlongPolyA\t100\twing\tgtf\tTranscriptFB554'''


def test_export_ol_no_map_tab_all_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', header=True)
    assert exp[0] == 'adaptor\tage\tbarcode\tcell\tdataType\tlabExpId\tlibBio\tlocalization\tmaxPeak\tnReads\torganism\tpath\tpoolId\treadStrand\treadType\treplicate\trnaExtract\trnaQuantity\ttissue\ttype\tview'
    assert exp[1] == '''ACTGAT(A)\tL3\tAR025\tanterior\trnaSeq\taWL3.2\t"5.8 ng/uL (30 nM) 08/04/2013"\tcell\t297\t37478754\tdmel\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\t2\tMATE1_SENSE\t2x75D\t2\tlongPolyA\t100\twing\tgtf\tTranscriptFB554'''


def test_replicates():
    """Test merged datasets"""
    i = Index('test/data/index.txt')
    i.set_format('test/data/format.json')
    dsid = i.format.get('id','id')
    i.open()
    reps = i.find_replicates(id="EWP.1,EWP.2")
    dataset = reps[0]
    others = reps[1:]
    merged = dataset.merge(others, dsid=dsid)
    for key in merged.get_meta_tags():
        vals = [getattr(d, key) for d in reps]
        if len(set(vals)) > 1:
            if key == dsid:
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
    i.lookup(id='aWL3.1,aWL3.2')
    i.remove(path='test/data/format.json', clear=True)
