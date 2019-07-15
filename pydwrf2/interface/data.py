import click

@click.group()
def cli():
    """Interact with pre-generated datasets for Mars."""
    pass

@cli.command()
@click.argument("dataset_name")
def load(dataset_name):
    from .. import datasets
    result = datasets.load_data(dataset_name)
    import json
    print(json.dumps(result, indent=2))

@cli.command()
@click.option("--sourcelist")
@click.option("--full",is_flag=True,default=False)
def list(sourcelist=None,full=False):
    from .. import datasets
    datasets.list_data(sourcelist,full)

if __name__ == "__main__":
    cli()