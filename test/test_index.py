"""Unit test for the Index class"""
import sys
import types
import pytest
import StringIO
from indexfile.index import Index, parse_line, to_str
from indexfile.config import config
@pytest.fixture(scope='session', autouse=True)
def setup_config():
    config.fileinfo.append('view')


def test_create_empty():
    """Create empty index"""
    i = Index()
    assert i is not None
    assert len(i) == 0


def test_create_path():
    """Create index from file path"""
    config.update("test/data/config.json")
    i = Index("test/data/index.txt")
    assert i is not None
    assert len(i) == 36


def test_create_wrong_path():
    """Create empty index"""
    with pytest.raises(IOError):
        i = Index('-')
    with pytest.raises(IOError):
        i = Index('test/data/index')


def test_create_file():
    """Create index from file handle"""
    fh = open("test/data/index.txt",'r')
    i = Index(fh)
    assert i is not None
    assert len(i) == 36


def test_create_stdin():
    """Create index from stdin"""
    fh = open("test/data/index.txt",'r')
    buf = fh.read().decode('utf-8')
    sys.stdin = StringIO.StringIO(buf)
    sys.stdin.seek(0)
    i = Index(sys.stdin)
    assert i is not None
    assert len(i) == 36


def test_create_defer_format():
    """Create index from file handle"""
    config.update("test/data/config.json")
    i = Index("test/data/index.txt")
    assert i is not None
    i.load()
    assert len(i) == 36


def test_create_empty_w_format():
    """Create empty index with custom format"""
    conf = {
        "id_desc": "labExpId",
        "fileinfo": [
            "path",
            "size",
            "md5"
        ],
        "format": {
            "col_sep": "\t",
            "tag_sep": " ",
            "kw_sep": "=",
            "kw_trail": ";"
        }
    }
    config.update(conf)
    i = Index()
    assert i is not None
    assert len(i) == 0


def test_load_empty():
    """Open empty index"""
    i = Index()
    assert i is not None
    with pytest.raises(AttributeError):
        i.load()


def test_load_string():
    """Test open with string parameter"""
    i = Index()
    assert i is not None
    i.fp = 'test/data/index.txt'
    i.load()
    assert len(i) == 36


def test_load_file():
    """Test open with file parameter"""
    i = Index()
    assert i is not None
    with open('test/data/index.txt','r') as f:
        i.fp = f
        i.load()
    assert len(i) == 36


def test_tsv_with_files():
    """Test open with file parameter"""
    config.update("test/data/config.json")
    i = Index('test/data/table_with_files.tsv')
    assert i is not None
    assert len(i) == 20
    assert len(i.lookup(type='bam')) == 20

def test_checksum():
    valid_checksum = '138b170830b04632f25da922442853a4'
    i = Index("test/data/index.txt")
    assert i.check_sum() == valid_checksum


def test_checksum_force():
    valid_checksum = '138b170830b04632f25da922442853a4'
    i = Index()
    i.fp = "test/data/index.txt"
    with pytest.raises(AttributeError):
        i.check_sum()
    assert i.check_sum(force=True) == valid_checksum


def test_checksum_empty():
    i = Index()
    with pytest.raises(AttributeError):
        i.check_sum()


def test_insert():
    """Test insertion into the index"""
    config.reset()
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
    assert len(dataset['test.txt']) == 2
    assert hasattr(dataset['test.txt'], 'path')
    assert hasattr(dataset['test.txt'], 'type')
    assert dataset['test.txt'].type == 'txt'


def test_insert_non_default_fileinfo():
    """Test insertion into the index with specified fileinfo"""
    i = Index()
    old_fileinfo = config.fileinfo
    config.fileinfo = [ 'path', 'type', 'date' ]
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
    assert len(dataset['test.txt']) == 3
    assert hasattr(dataset['test.txt'], 'path')
    assert hasattr(dataset['test.txt'], 'type')
    assert hasattr(dataset['test.txt'], 'date')
    assert dataset['test.txt'].type == 'txt'
    assert dataset['test.txt'].date == '20150304'
    config.fileinfo = old_fileinfo


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
    assert len(dataset['test.txt']) == 2
    assert hasattr(dataset['test.txt'], 'path')
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
    assert len(dataset['test.txt']) == 2
    assert hasattr(dataset['test.txt'], 'path')
    assert hasattr(dataset['test.txt'], 'type')
    assert dataset['test.txt'].type == 'text'

def test_add_file_external():
    index = '''.\tage=-; cell=Neutrophils; dataType=RNA-Seq; dateSubmittedFirst=2012-10-17T09:49:23+0200; donorId=C000XW; ethnicity=NA; lab=MPIMG; labExpId=ERR180946; labProtocolId=C000XWB1; libProtocol=I_bc_pelib_858; localization="Primary Cell"; quality=phred; readStrand=MATE2_SENSE; readType=2x76D; rnaExtract=total; seqPlatform=ILLUMINA; seqRun=1; sex=Male; sraSampleAccession=ERS150362; sraStudyAccession=ERP001664; tissue="Cord blood";'''
    config.update("test/data/tsv_config.json")
    config.fileinfo.append('view')
    i = Index()
    i.insert(**parse_line(index))
    i.insert(id="ERR180946", path="/users/rg/epalumbo/projects/BluePrint/reads/20130805/data/ERR180946_1.fastq.gz", view="FastqRd1",type="fastq")
    assert i.export().next() == '''/users/rg/epalumbo/projects/BluePrint/reads/20130805/data/ERR180946_1.fastq.gz\tage=-; cell=Neutrophils; dataType=RNA-Seq; dateSubmittedFirst=2012-10-17T09:49:23+0200; donorId=C000XW; ethnicity=NA; lab=MPIMG; labExpId=ERR180946; labProtocolId=C000XWB1; libProtocol=I_bc_pelib_858; localization="Primary Cell"; quality=phred; readStrand=MATE2_SENSE; readType=2x76D; rnaExtract=total; seqPlatform=ILLUMINA; seqRun=1; sex=Male; sraSampleAccession=ERS150362; sraStudyAccession=ERP001664; tissue="Cord blood"; type=fastq; view=FastqRd1;'''


def test_lookup_simple_dataset():
    config.reset()
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
    config.update("test/data/config.json")
    i = Index('test/data/index.txt')
    assert i.datasets.get('WLP.2') is not None
    selected = i.lookup(id='WLP.2')
    assert selected.datasets != i.datasets
    assert len(selected.datasets) == 1
    dataset = selected.datasets.get('WLP.2')
    assert dataset is not None
    dataset.id = 'WLP.2'


def test_lookup_more_types_index_id():
    """Test export"""
    config.update("test/data/config.json")
    i = Index('test/data/index_gfs.txt')
    result = i.lookup(id='WWP.1')
    assert result.export().next()[0] != '.'


def test_lookup_one_type_index():
    """Test export"""
    i = Index('test/data/index_gtfs.txt')
    result = i.lookup(type='gtf')
    assert result.export().next()[0] != '.'


def test_lookup_more_types_index():
    """Test export"""
    i = Index('test/data/index_one_gfs.txt')
    result = i.lookup(type='gtf')
    assert result != None
    assert result.datasets != {}
    assert result.export().next()[0] != '.'


def test_lookup_full_index():
    """Test export"""
    i = Index('test/data/index.txt')
    result = i.lookup(type='gtf')
    assert result.export().next()[0] != '.'


def test_remove_dataset():
    config.reset()
    i = Index()
    i.insert(id='1', age=65, path='test.txt', type='txt')
    i.remove(id='1')
    assert len(i.datasets) == 0
    setup_config()


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


def test_export_w_map():
    """Test export"""
    config.update('test/data/config.json')
    i = Index('test/data/index.txt')
    exp = i.export(map_keys=True)
    assert isinstance(exp, types.GeneratorType)
    assert 'LIBRARY_ID' in exp.next()
    assert len(list(exp)) == 215


def test_export_w_map_one_tag():
    """Test export"""
    i = Index('test/data/index.txt')
    exp = i.export(map_keys=True, tags='id')
    assert isinstance(exp, types.GeneratorType)
    assert 'LIBRARY_ID' in exp.next()
    assert len(list(exp)) == 215


def test_export_w_map_oneline():
    """Test export one known line"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(map_keys=True)
    assert exp.next() == '''aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tLIBRARY_ID=aWL3.2; RNA_quantity=100; barcode=AR025; cell=anterior; dataType=rnaSeq; developmental_point=L3; library_Bioanalyser="5.8 ng/uL (30 nM) 08/04/2013"; localization=cell; max_peak=297; n_sequences=37478754; organism=dmel; pool_ID=2; readStrand=MATE1_SENSE; readType=2x75D; replicate=2; rnaExtract=longPolyA; sequence=ACTGAT(A); tissue=wing; type=gtf; view=TranscriptFB554;'''


def test_export_no_map():
    """Test export"""
    i = Index('test/data/index.txt')
    exp = i.export()
    first = exp.next()
    assert 'labExpId' in first
    assert 'fileinfo' not in first
    assert len(list(exp)) == 215


def test_export_no_format_no_map():
    """Test export"""
    config.reset()
    i = Index()
    i.insert(id="myId", path="test/data/index.txt", type="text", view="TxtFile")
    exp = list(i.export(output_format='tsv', tags=['id']))
    assert exp[0] == 'myId'
    assert len(exp) == 1
    setup_config()


def test_export_no_map_tab_tags_no_miss():
    """Test export without missing values"""
    config.update('test/data/config.json')
    i = Index('test/data/index.txt')
    exp = i.export(output_format='tsv', tags=['id', 'path'],
                   hide_missing=True)
    assert exp.next() == 'EL3.1\t/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1_5355_ATCACG.minusRaw.bigwig'
    assert len(list(exp)) == 199


def test_export_no_map_tab_repeated_tags():
    """Test export tab output with repeated tags"""
    i = Index('test/data/index.txt')
    exp = i.export(output_format='tsv', tags=['id', 'id', 'path'],
                   hide_missing=True)
    assert exp.next() == 'EL3.1\tEL3.1\t/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1_5355_ATCACG.minusRaw.bigwig'
    assert len(list(exp)) == 199


def test_export_no_map_tab_path_template():
    """Test export tab output with path template"""
    i = Index('test/data/index.txt')
    exp = i.export(output_format='tsv', tags=['path','{dirname}/{id}.{view}.{ext}'],
                   hide_missing=True)
    assert exp.next() == '/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1_5355_ATCACG.minusRaw.bigwig\t/users/rg/epalumbo/projects/ERC/fly/bp.pipeline/EL3.1/EL3.1.MinusRawSignal.bigwig'
    assert len(list(exp)) == 199


def test_export_oneline_no_map():
    """Test export one known line"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export()
    assert exp.next() == '''aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tadaptor=ACTGAT(A); age=L3; barcode=AR025; cell=anterior; dataType=rnaSeq; labExpId=aWL3.2; libBio="5.8 ng/uL (30 nM) 08/04/2013"; localization=cell; maxPeak=297; nReads=37478754; organism=dmel; poolId=2; readStrand=MATE1_SENSE; readType=2x75D; replicate=2; rnaExtract=longPolyA; rnaQuantity=100; tissue=wing; type=gtf; view=TranscriptFB554;'''


def test_export_ol_no_map_tab_tags():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(output_format='tsv', tags=['id', 'path'])
    assert exp.next() == 'aWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_path():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(output_format='tsv', tags=['path'])
    assert exp.next() == 'aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_tags_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(output_format='tsv', tags=['id', 'path'],
                   header=True)
    assert exp.next() == 'labExpId\tpath'
    assert exp.next() == 'aWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_repeated_tags_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(output_format='tsv', tags=['id', 'id', 'path'],
                   header=True)
    assert exp.next() == 'labExpId\tlabExpId\tpath'
    assert exp.next() == 'aWL3.2\taWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tsv_all():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(output_format='tsv')
    assert exp.next() == '''ACTGAT(A)\tL3\tAR025\tanterior\trnaSeq\taWL3.2\t"5.8 ng/uL (30 nM) 08/04/2013"\tcell\t297\t37478754\tdmel\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\t2\tMATE1_SENSE\t2x75D\t2\tlongPolyA\t100\twing\tgtf\tTranscriptFB554'''


def test_export_ol_no_map_csv_all():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(output_format='csv')
    assert exp.next() == '''ACTGAT(A),L3,AR025,anterior,rnaSeq,aWL3.2,"5.8 ng/uL (30 nM) 08/04/2013",cell,297,37478754,dmel,aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf,2,MATE1_SENSE,2x75D,2,longPolyA,100,wing,gtf,TranscriptFB554'''


def test_export_ol_no_map_tab_all_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    exp = i.export(output_format='tsv', header=True)
    assert exp.next() == 'adaptor\tage\tbarcode\tcell\tdataType\tlabExpId\tlibBio\tlocalization\tmaxPeak\tnReads\torganism\tpath\tpoolId\treadStrand\treadType\treplicate\trnaExtract\trnaQuantity\ttissue\ttype\tview'
    assert exp.next() == '''ACTGAT(A)\tL3\tAR025\tanterior\trnaSeq\taWL3.2\t"5.8 ng/uL (30 nM) 08/04/2013"\tcell\t297\t37478754\tdmel\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\t2\tMATE1_SENSE\t2x75D\t2\tlongPolyA\t100\twing\tgtf\tTranscriptFB554'''


def test_replicates():
    """Test merged datasets"""
    config.update("test/data/config.json")
    i = Index('test/data/index.txt')
    dsid = config.id_desc
    reps = list(i.find_replicates(id="EWP.1,EWP.2"))
    dataset = reps[0]
    others = reps[1:]
    merged = dataset.merge(others)
    for key in merged.keys():
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
    i.insert(id='aWL3.1,aWL3.2',
             path='test/data/config.json',
             type='json',
             view='json')
    i.lookup(id='aWL3.1,aWL3.2')
    i.remove(path='test/data/config.json', clear=True)


def test_format():
    """Convert dictionary to indexfile string"""
    info = {'id': '1', 'path': 'test.txt', 'view': 'text', 'type': 'txt'}
    out = to_str(**info)
    assert out == "id=1; path=test.txt; type=txt; view=text;"
    # with replicates
    info = {'id': ['1', '2'], 'path': ['test1.txt', 'test2.txt'],
            'view': ['text', 'text'], 'type': ['txt', 'txt']}
    out = to_str(**info)
    assert out == '''id=1,2; path=test1.txt,test2.txt; type=txt,txt; view=text,text;'''

def test_issue_37():
    index = '''.\tid=1; SMPTHNTS="6 pieces; mucosa=3; muscularis=1; only muscle useful"; SMRDTTL=91315246; SMRIN=7;'''
    line = parse_line(index)
    assert line['id'] == '1'
    assert line['SMPTHNTS'] == '"6 pieces; mucosa=3; muscularis=1; only muscle useful"'
    assert line['SMRDTTL'] == '91315246'
    assert line['SMRIN'] == '7'

def test_issue_38():
    line = dict()
    line['id'] = '1'
    line['SMPTHNTS'] = '2 pieces, 9x6 & 10x9mm; myofibers pale compared to other heart specimen; BSS notes ""mislabeled solution""'
    line['SMRDTTL'] = '91315246'
    line['SMRIN'] = '7'
    out = to_str(**line)
    print out
    assert out == '''SMPTHNTS="2 pieces, 9x6 & 10x9mm; myofibers pale compared to other heart specimen; BSS notes ""mislabeled solution"""; SMRDTTL=91315246; SMRIN=7; id=1;'''

def test_issue_39():
    index = '''.\tid=1; SMPTHNTS="6 pieces mucosa=3; muscularis=1; only muscle useful"; SMRDTTL=91315246; SMRIN=7;'''
    line = parse_line(index)
    assert line['id'] == '1'
    assert line['SMPTHNTS'] == '"6 pieces mucosa=3; muscularis=1; only muscle useful"'
    assert line['SMRDTTL'] == '91315246'
    assert line['SMRIN'] == '7'
