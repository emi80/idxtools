import click
import indexfile
from indexfile import *
from indexfile.cli import *

@click.command(cls=IndexfileCLI, context_settings=CONTEXT_SETTINGS)
@click.option('-i', '--index', envvar=DEFAULT_ENV_INDEX, type=click.File('r'), default='-', help='The input index file.')
@click.option('-f', '--format', envvar=DEFAULT_ENV_FORMAT, type=click.Path(), default=None, help='Index format specifications in JSON or YAML format.', show_default=True)
@click.option('--loglevel', type=click.Choice(log_levels()), default=config.loglevel, help='Set the log level to the desired level.', show_default=True)
@click.version_option(indexfile.__version__)
@click.pass_context
def cli(ctx, index, format, loglevel):
    """The indexfile cli"""
    config.update(format)
    ctx.index = Index(index)
    ctx.loglevel = loglevel

if __name__ == "__main__":
    cli()
