"""
Add or update metadata information to the index

Usage: %s [options] [<metadata>...]

Options:
  -l --metadata-list <list>     List of metadata information to be used.
  -a --attributes <attributes>  List of attribute names referring to the metadata
                                list.
  -u --update                   Update information for existing datasets
  -f --force                    Only works in combination with --update. Add non-existing keys to the dataset.
"""
import re
import click
import indexfile

def attributes_cb(ctx, param, value):
    if value:
        try:
            attrs = value.split(',')
            return attrs
        except ValueError:
            raise click.BadParameter('attributes must be comma separated')

    else:
        return []

@click.command()
@click.option('-l', '--metadata-list', type=click.File('r'), default='-', help='List of metadata information to be used.')
@click.option('-a', '--attributes', callback=attributes_cb, help='List of attribute names referring to the metadata list')
@click.option('-u', '--update', is_flag=True, help='Update information for existing datasets', default=False, show_default=True)
@click.option('-f', '--force', is_flag=True, help='Only works in combination with --update. Add non-existing keys to the dataset.',
              default=False, show_default=True)
@click.argument('metadata', nargs=-1)
@click.pass_context
def cli(ctx, metadata_list, attributes, update, force, metadata):
    """Add or update metadata information to the index"""
    log = indexfile.get_logger(__name__)
    kwargs = {}
    index = ctx.parent.index
    if not metadata and metadata_list:
        for file_ in metadata_list.readlines():
            file_ = file_.strip().split('\t')
            if not attributes:
                attributes = file_
                continue
            assert len(file_) == len(attributes), 'The number of attributes in the metadata list is different from the one given in the command line'
            for i, k in enumerate(attributes):
                kwargs[k] = file_[i]

            index.insert(update=update, addkeys=force, **kwargs)

        index.save()
    elif metadata:
        for md in metadata:
            match_ = re.match('(?P<key>[^=<>!]*)=(?P<value>.*)', md)
            kwargs[match_.group('key')] = match_.group('value')

        index.insert(update=update, addkeys=force, **kwargs)
        index.save()
    else:
        docopt(__doc__ % command, argv='--help')
