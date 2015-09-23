"""
Select datasets using query strings. Examples of valid strings are: 'sex=M' and 'lab=CRG'.
Multiple fields in a query are joind with an 'AND'.
"""
import os
import re
import sys
import click
import errno
from indexfile import Index, OUTPUT_FORMATS

# callbacks
def tags_cb(ctx, param, value):
    if value:
        try:
            tags = value.split(',')
            return tags
        except ValueError:
            raise click.BadParameter('tags must be comma separated')

    else:
        return []


def show_tags_cb(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    sys.stdout.write('\n'.join(sorted(ctx.parent.index.all_tags())))
    ctx.exit()


@click.command()
@click.option('-a', '--absolute-path', is_flag=True, help='Specify if absolute path should be returned')
@click.option('-c', '--count', is_flag=True, help='Return the number of files/datasets')
@click.option('-e', '--exact', is_flag=True, help='Specifies whether to perform exact match for searches')
@click.option('-m', '--map-keys', is_flag=True, help='Specify if mapping information for key should be used for output')
@click.option('-t', '--tags', callback=tags_cb, help='Specify the attributes to be written to output')
@click.option('-s', '--show-missing', is_flag=True, default=False, help='Show lines with missing values')
@click.option('--all-tags', is_flag=True, default=False, help='Show tags list', callback=show_tags_cb, is_eager=True, expose_value=False)
@click.option('-o', '--output', type=click.File('w'), default='-', help='The output file')
@click.option('-f', '--output-format', type=click.Choice(OUTPUT_FORMATS), default='index', help='The output format', envvar='IDX_OUTPUT_FORMAT')
@click.option('--header', is_flag=True, help='Output header when selecting tags')
@click.argument('query', nargs=-1)
@click.pass_context
def cli(ctx, absolute_path, count, exact, map_keys, tags, show_missing, output, output_format, header, query):
    """Show index contents and filter based on query terms"""
    index = ctx.parent.index
    indices = []
    if query:
        list_sep = '[:\\s]'
        kwargs = {}
        for qry in query:
            match = re.match('(?P<key>[^=<>!]*)=(?P<value>.*)', qry, re.DOTALL)
            kwargs[match.group('key')] = match.group('value')
            if re.search(list_sep, kwargs[match.group('key')], re.MULTILINE):
                kwargs[match.group('key')] = re.split(list_sep, match.group('value'))

        indices.append(index.lookup(exact=exact, **kwargs))
    else:
        indices.append(index)
    for i in indices:
        if isinstance(i, Index):
            if count and not tags:
                output.write('%s%s' % (len(i), os.linesep))
                return
            kwargs = {'header': header,
             'output_format': output_format,
             'tags': tags,
             'absolute': absolute_path,
             'hide_missing': not show_missing}
            if not map_keys:
                kwargs['map'] = None
            indexp = i.export(**kwargs)
            if count:
                output.write('%s%s' % (len(list(indexp)), os.linesep))
                return
            for line in indexp:
                output.write('%s%s' % (line, os.linesep))
