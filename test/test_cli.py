""" Tests for the cli module """

import os
import click
import pytest
import indexfile.cli
from indexfile import config
from click.testing import CliRunner
from indexfile.cli.indexfile_main import cli as main_cli

oneline_output = ' '.join([
    'aWL3.2/aWL3.2_4204_ACTGAT_transcript.gtf\tadaptor=ACTGAT(A);',
    'age=L3; barcode=AR025; cell=anterior; dataType=rnaSeq; labExpId=aWL3.2;' ,
    'libBio="5.8 ng/uL (30 nM) 08/04/2013"; localization=cell; maxPeak=297;',
    'nReads=37478754; organism=dmel; poolId=2; readStrand=MATE1_SENSE;',
    'readType=2x75D; replicate=2; rnaExtract=longPolyA; rnaQuantity=100;',
    'tissue=wing; type=gtf; view=TranscriptFB554;\n'
])

def test_file_config(tmpdir, monkeypatch):
    """ Load configuration from file """

    # prepare yaml config file
    monkeypatch.chdir(str(tmpdir))
    with open('.indexfile.yml', 'w+') as cfg:
        cfg.write("index:  test/data/index.txt\n")
        cfg.write("format: test/data/format.json\n")

    indexfile.cli.CONTEXT_SETTINGS = {}
    indexfile.cli._read_config()
    default_map = indexfile.cli.CONTEXT_SETTINGS.get('default_map')
    assert default_map is not None
    assert default_map.get('index') == 'test/data/index.txt'
    assert default_map.get('format') == 'test/data/format.json'


def test_file_config_recursive(tmpdir, monkeypatch):
    """ Load configuration from file walking up directory tree"""

    # prepare yaml config file
    _dir = os.path.join(str(tmpdir), 'dir1')
    os.mkdir(_dir)
    monkeypatch.chdir(_dir)
    with open('.indexfile.yml', 'w+') as cfg:
        cfg.write("index:  test/data/index.txt\n")
        cfg.write("format: test/data/format.json\n")


    indexfile.cli.CONTEXT_SETTINGS = {}
    indexfile.cli._read_config()
    default_map = indexfile.cli.CONTEXT_SETTINGS.get('default_map')
    assert default_map is not None
    assert default_map.get('index') == 'test/data/index.txt'
    assert default_map.get('format') == 'test/data/format.json'


def test_file_not_found_config(tmpdir, monkeypatch):
    """ Load configuration from environment variables """

    monkeypatch.chdir(str(tmpdir))
    indexfile.cli.CONTEXT_SETTINGS = {}
    indexfile.cli._read_config()
    default_map = indexfile.cli.CONTEXT_SETTINGS.get('default_map')
    assert default_map is None


def test_env_config():
    """ Load configuration from environment variables """

    env = {}
    env['IDX_FILE'] = 'test/data/index_oneline.txt'
    env['IDX_FORMAT'] = 'test/data/config.json'

    runner = CliRunner(env=env)
    result = runner.invoke(main_cli, ['show'])

    assert result.exit_code == 0
    assert result.exception == None
    assert result.output == oneline_output


def test_cli_args_config():
    """ Load configuration from command line arguments """

    args = [
        '--index',
        'test/data/index_oneline.txt',
        '--format',
        'test/data/config.json',
        'show'
    ]

    runner = CliRunner()
    result = runner.invoke(main_cli, args)

    assert result.exit_code == 0
    assert result.exception == None
    assert result.output == oneline_output


def test_add_multiple_files(tmpdir):
    """ Test insertion of multiple files """

    # expected lines
    expected = 'test_1.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd1;\n'
    expected += 'test_2.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd2;\n'

    # reset config
    config.reset()
    config.fileinfo.append('view')

    # prepare input files and options
    idxfile = '%s/index.txt' % tmpdir
    filelist = '%s/list.tsv' % tmpdir
    with open(idxfile, "w+") as i:
        i.write('.\tid=1; age=10; sex=M;\n')
    with open(filelist, 'w+') as fli:
        fli.write("\t".join(['test_1.fastq', '1', 'FqRd1', 'fastq']) + "\n")
        fli.write("\t".join(['test_2.fastq', '1', 'FqRd2', 'fastq']) + "\n")
    attrs = "path,id,view,type"

    env = {}
    env['IDX_FILE'] = idxfile
    env['IDX_FORMAT'] = None

    runner = CliRunner(env=env)

    args = [ 'add', '-a', attrs, '-l', filelist ]
    result = runner.invoke(main_cli, args)

    assert result.exit_code == 0
    assert result.exception == None


    args = [ 'show' ]
    result = runner.invoke(main_cli, args)

    assert result.exit_code == 0
    assert result.exception == None
    assert result.output == expected


def test_add_multiple_files_w_header(tmpdir):
    """ Test insertion of multiple files """

    # expected lines
    expected = 'test_1.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd1;\n'
    expected += 'test_2.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd2;\n'

    # reset config
    config.reset()
    config.fileinfo.append('view')

    # prepare input files and options
    idxfile = '%s/index.txt' % tmpdir
    filelist = '%s/list.tsv' % tmpdir
    with open(idxfile, "w+") as i:
        i.write('.\tid=1; age=10; sex=M;\n')
    with open(filelist, 'w+') as fli:
        fli.write("\t".join(['path','id','view','type']) + "\n")
        fli.write("\t".join(['test_1.fastq', '1', 'FqRd1', 'fastq']) + "\n")
        fli.write("\t".join(['test_2.fastq', '1', 'FqRd2', 'fastq']) + "\n")

    env = {}
    env['IDX_FILE'] = idxfile
    env['IDX_FORMAT'] = None

    runner = CliRunner(env=env)

    args = [ 'add', '-l', filelist ]
    result = runner.invoke(main_cli, args)

    assert result.exit_code == 0
    assert result.exception == None


    args = [ 'show' ]
    result = runner.invoke(main_cli, args)

    assert result.exit_code == 0
    assert result.exception == None
    assert result.output == expected
