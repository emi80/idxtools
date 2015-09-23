"""
Command line interface to the IndexFile API
"""
import os
import yaml
import glob
import click

__all__ = [
    'IndexfileCLI', 'CONTEXT_SETTINGS', 'DEFAULT_ENV_INDEX', 'DEFAULT_ENV_FORMAT'
]

IGNORE_COMMANDS = [
    '__init__',
    'indexfile_main',
]

COMMANDS_FOLDER = os.path.dirname(__file__)

PREFIX = 'indexfile_'

COMMAND_ALIASES = {
    'show': ['view'],
    'remove': ['rm'],
    'update': ['add']
}

# environment variables
DEFAULT_ENV_PREFIX = 'IDX'
DEFAULT_ENV_INDEX = DEFAULT_ENV_PREFIX + '_FILE'
DEFAULT_ENV_FORMAT = DEFAULT_ENV_PREFIX + '_FORMAT'

# load settings from file
DEFAULT_SETTINGS_FILE = '.indexfile.yml'
CONTEXT_SETTINGS = {}

# utility methods
def _walk_up(bottom='.'):
    """
    mimic os.walk, but walk 'up'
    instead of down the directory tree
    """
    bottom = os.path.realpath(bottom)
    # get files in current dir
    names = os.listdir(bottom)
    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(bottom, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    yield bottom, dirs, nondirs
    new_path = os.path.realpath(os.path.join(bottom, '..'))
    # see if we are at the top
    if new_path == bottom:
        return
    for x in _walk_up(new_path):
        yield x

def _read_config():
    fp = None
    for c, d, f in _walk_up():
        if DEFAULT_SETTINGS_FILE in f:
            fp = os.path.join(c, DEFAULT_SETTINGS_FILE)
            break
    if fp:
        with open(fp) as cfg:
            CONTEXT_SETTINGS['default_map'] = yaml.load(cfg)

def _get_aliases_str(name):
    if name in COMMAND_ALIASES:
       return " (aliases: {})".format(', '.join([name] + COMMAND_ALIASES[name]))
    return ''

# main multicommand class
class IndexfileCLI(click.MultiCommand):

    def list_commands(self, ctx):
        """List available commands"""
        rv = []
        cmds = glob.glob('{0}/*.py'.format(COMMANDS_FOLDER))
        for cmd in cmds:
            mod = os.path.basename(cmd).replace('.py', '')
            if mod in IGNORE_COMMANDS:
                continue
            name = mod.replace(PREFIX, '')
            rv.append(name)

        rv.sort()
        return rv

    def get_command(self, ctx, name):
        """Load command from files"""
        ns = {}
        commands = self.list_commands(ctx) + [ i for v in COMMAND_ALIASES.values() for i in v ]
        if name not in commands:
            return None
        for k, v in COMMAND_ALIASES.iteritems():
            if name in v:
                name = k
        fn = os.path.join(COMMANDS_FOLDER, PREFIX + name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        ns['cli'].help += _get_aliases_str(name)
        return ns['cli']

# do stuff on import
_read_config()
