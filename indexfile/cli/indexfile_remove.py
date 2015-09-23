"""
Remove files and/or datasets from the index. Query can be a file path or a string
like 'id=ID001' or 'type=bam'.
"""
import click

@click.command()
@click.option('-c', '--clear', is_flag=True, help='Remove a dataset entry in the index if it does not contain any more files', 
              default=False, show_default=True)
@click.argument('query', nargs=-1)
@click.pass_context
def cli(ctx, clear, query):
    """Remove files and/or datasets from the index"""
    index = ctx.parent.index
    for qry in query:
        if '=' in qry:
            kwargs = dict([qry.split('=')])
            kwargs['clear'] = clear
            index.remove(**kwargs)
        else:
            index.remove(path=query, clear=clear)
        index.save()
