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
    assert type(exp) == list
    assert len(exp) == 36
    assert 'LIBRARY_ID' in exp[0]


def test_export_oneline():
    """Test export one known line"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export()
    assert exp[0] == '''aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tLIBRARY_ID=aWL3.2; RNA_quantity=100; barcode=AR025; cell=anterior; dataType=rnaSeq; developmental_point=L3; fileinfo=path,size,md5,type,view,submittedDataVersion; library_Bioanalyser="5.8 ng/uL (30 nM) 08/04/2013"; localization=cell; max_peak=297; n_sequences=37478754; organism=dmel; pool_ID=2; readStrand=MATE1_SENSE; readType=2x75D; replicate=2; rnaExtract=longPolyA; sequence=ACTGAT(A); tissue=wing; type=gtf; view=TranscriptFB554;'''


def test_export_no_map():
    """Test export"""
    i = Index('test/data/index.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None)
    assert len(exp) == 36
    assert 'labExpId' in exp[0]


def test_export_oneline_no_map():
    """Test export one known line"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None)
    assert exp[0] == '''aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tadaptor=ACTGAT(A); age=L3; barcode=AR025; cell=anterior; dataType=rnaSeq; fileinfo=path,size,md5,type,view,submittedDataVersion; labExpId=aWL3.2; libBio="5.8 ng/uL (30 nM) 08/04/2013"; localization=cell; maxPeak=297; nReads=37478754; organism=dmel; poolId=2; readStrand=MATE1_SENSE; readType=2x75D; replicate=2; rnaExtract=longPolyA; rnaQuantity=100; tissue=wing; type=gtf; view=TranscriptFB554;'''


def test_export_ol_no_map_tab_tags():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['id', 'path'])
    assert exp[0] == 'aWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'

def test_export_ol_no_map_tab_tags_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', tags=['id', 'path'],
                   header=True)
    assert exp[0] == 'id\tpath'
    assert exp[1] == 'aWL3.2\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf'


def test_export_ol_no_map_tab_all():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab')
    assert exp[0] == '''"5.8 ng/uL (30 nM) 08/04/2013"\tcell\tACTGAT(A)\tdmel\tL3\tAR025\t2x75D\taWL3.2\t2\tanterior\t297\tlongPolyA\twing\t2\t100\tMATE1_SENSE\t37478754\trnaSeq\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tgtf\tTranscriptFB554'''


def test_export_ol_no_map_tab_all_header():
    """Test export"""
    i = Index('test/data/index_oneline.txt')
    assert i is not None
    i.set_format('test/data/format.json')
    i.open()
    exp = i.export(map=None, export_type='tab', header=True)
    assert exp[0] == 'maxPeak\treadType\ttissue\tlibBio\tcell\tdataType\treplicate\tnReads\ttype\tlocalization\tadaptor\tlabExpId\tbarcode\trnaExtract\tpath\tage\trnaQuantity\treadStrand\tpoolId\torganism\tview'
    assert exp[1] == '''"5.8 ng/uL (30 nM) 08/04/2013"\tcell\tACTGAT(A)\tdmel\tL3\tAR025\t2x75D\taWL3.2\t2\tanterior\t297\tlongPolyA\twing\t2\t100\tMATE1_SENSE\t37478754\trnaSeq\taWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tgtf\tTranscriptFB554'''


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
