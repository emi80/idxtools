""" Tests for the cli module """

import os
import pytest
import indexfile.cli

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


# def test_env_config():
#     """ Load configuration from environment variables """
#     env['IDX_FILE'] = 'env/test/data/index.txt'
#     env['IDX_FORMAT'] = 'env/test/data/format.json'
#
#     config = load_config()
#
#     assert config['index'] == env['IDX_FILE']
#     assert config['format'] == env['IDX_FORMAT']
#
#
# def test_file_config(tmpdir):
#     """ Load configuration from file """
#
#     # prepare yaml config file
#     configfile = '{0}/.indexfile.yml'.format(tmpdir)
#     with open(configfile, 'w+') as cfg:
#         cfg.write("index:  test/data/index.txt\n")
#         cfg.write("format: test/data/format.json\n")
#
#     config = load_config(path=str(tmpdir))
#
#     assert config['index'] == 'test/data/index.txt'
#     assert config['format'] == 'test/data/format.json'
#
#
# def test_file_config_recursive(tmpdir):
#     """ Load configuration from file walking up directory tree"""
#
#     # prepare yaml config file
#     configfile = '{0}/.indexfile.yml'.format(tmpdir)
#     with open(configfile, 'w+') as cfg:
#         cfg.write("index:  test/data/index.txt\n")
#         cfg.write("format: test/data/format.json\n")
#
#     _dir = os.path.join(str(tmpdir), 'dir1')
#     os.mkdir(_dir)
#
#     config = load_config(path=_dir)
#
#     assert config['index'] == 'test/data/index.txt'
#     assert config['format'] == 'test/data/format.json'
#
#
# def test_cli_args_config():
#     """ Load configuration from command line arguments """
#
#     args = docopt(doc=im.__doc__ % ('idxtools', 'idxtools'), argv=[
#         'idxtools',
#         '--index',
#         '../test/data/index.txt',
#         '--format',
#         '../test/data/format.json'
#     ])
#
#     args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])
#
#     config = load_config(args=args)
#
#     assert config['index'] == '../test/data/index.txt'
#     assert config['format'] == '../test/data/format.json'
#
#
# def test_file_not_found_config(tmpdir):
#     """ Load configuration from environment variables """
#     env['IDX_FILE'] = 'env/test/data/index.txt'
#     env['IDX_FORMAT'] = 'env/test/data/format.json'
#
#     configfile = '{0}/idxtool.yml'.format(tmpdir)
#
#     config = load_config(path=configfile)
#
#     assert config['index'] == env['IDX_FILE']
#     assert config['format'] == env['IDX_FORMAT']
#
#
# def test_add_multiple_files(tmpdir):
#     """ Test insertion of multiple files """
#     # reset env
#     del env['IDX_FORMAT']
#
#     # prepare input files and options
#     idxfile = '%s/index.txt' % tmpdir
#     filelist = '%s/list.tsv' % tmpdir
#     with open(idxfile, "w+") as i:
#         i.write('.\tid=1; age=10; sex=M;\n')
#     with open(filelist, 'w+') as fli:
#         fli.write("\t".join(['test_1.fastq', '1', 'FqRd1', 'fastq']) + "\n")
#         fli.write("\t".join(['test_2.fastq', '1', 'FqRd2', 'fastq']) + "\n")
#     attrs = "path,id,view,type"
#     env['IDX_FILE'] = idxfile
#
#     # expected lines
#     expected = 'test_1.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd1;\n'
#     expected += 'test_2.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd2;\n'
#
#
#     # run commands
#     command = 'idxtools add -a %s -l %s' % (attrs, filelist)
#     call(command, shell=True, stdout=PIPE)
#     command_line = "idxtools show"
#     out = Popen(command_line, stdout=PIPE, shell=True).communicate()[0]
#
#     assert out == expected
