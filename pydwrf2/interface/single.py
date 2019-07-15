import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("directory")
@click.argument("output_filename")
def index(directory, output_filename):
    from ..wrf import common as wc
    _ = wc._index(directory, output_filename)

if __name__=="__main__":
    cli()