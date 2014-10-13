""" Tests for the cli module """

# pylint: disable=E0611
from indexfile.cli import default_config, load_config
from os import (
    environ as env
)
from docopt import docopt
import indexfile.cli.indexfile_main as im
from subprocess import call, Popen, PIPE


def test_default_config():
    """ Load default configuration """
    default = default_config()
    config = load_config()

    assert config == default


def test_env_config():
    """ Load configuration from environment variables """
    env['IDX_FILE'] = 'env/test/data/index.txt'
    env['IDX_FORMAT'] = 'env/test/data/format.json'

    config = load_config()

    assert config['index'] == env['IDX_FILE']
    assert config['format'] == env['IDX_FORMAT']


def test_file_config(tmpdir):
    """ Load configuration from file """

    # prepare yaml config file
    configfile = '{0}/indexfile.yml'.format(tmpdir)
    with open(configfile, 'w+') as cfg:
        cfg.write("index:  test/data/index.txt\n")
        cfg.write("format: test/data/format.json\n")

    config = load_config(path=configfile)

    assert config['index'] == 'test/data/index.txt'
    assert config['format'] == 'test/data/format.json'


def test_cli_args_config():
    """ Load configuration from command line arguments """

    args = docopt(doc=im.__doc__ % ('idxtools', 'idxtools'), argv=[
        'idxtools',
        '--index',
        '../test/data/index.txt',
        '--format',
        '../test/data/format.json'
    ])

    args = dict([(k.replace('-', ''), v) for k, v in args.iteritems()])

    config = load_config(args=args)

    assert config['index'] == '../test/data/index.txt'
    assert config['format'] == '../test/data/format.json'


def test_file_not_found_config(tmpdir):
    """ Load configuration from environment variables """
    env['IDX_FILE'] = 'env/test/data/index.txt'
    env['IDX_FORMAT'] = 'env/test/data/format.json'

    configfile = '{0}/idxtool.yml'.format(tmpdir)

    config = load_config(path=configfile)

    assert config['index'] == env['IDX_FILE']
    assert config['format'] == env['IDX_FORMAT']


def test_add_multiple_files(tmpdir):
    """ Test insertion of multiple files """
    # reset env
    del env['IDX_FORMAT']

    # prepare input files and options
    idxfile = '%s/index.txt' % tmpdir
    filelist = '%s/list.tsv' % tmpdir
    with open(idxfile, "w+") as i:
        i.write('.\tid=1; age=10; sex=M;\n')
    with open(filelist, 'w+') as fli:
        fli.write("\t".join(['test_1.fastq', '1', 'FqRd1', 'fastq']) + "\n")
        fli.write("\t".join(['test_2.fastq', '1', 'FqRd2', 'fastq']) + "\n")
    attrs = "path,id,view,type"
    env['IDX_FILE'] = idxfile

    # expected lines
    expected = 'test_2.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd2;\n'
    expected += 'test_1.fastq\tage=10; id=1; sex=M; type=fastq; view=FqRd1;\n'

    # run commands
    command = 'idxtools add -a %s -l %s' % (attrs, filelist)
    call(command, shell=True, stdout=PIPE)
    command_line = "idxtools show"
    out = Popen(command_line, stdout=PIPE, shell=True).communicate()[0]

    assert out == expected
