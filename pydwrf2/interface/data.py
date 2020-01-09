import click


@click.group()
def cli():
    """Interact with pre-generated datasets for Mars."""


@cli.command()
@click.argument("dataset_name")
@click.option("--remote", default=None)
def load(dataset_name, remote=None):
    """Load a dataset given the name

    Args:
        dataset_name : The name of the data to load
    Prints:
        The json entry for the dataset.
    """
    from .. import datasets

    result = datasets.load_data(dataset_name, remote=remote)
    import json

    print(json.dumps(result, indent=2))


@cli.command()
@click.option("--remote")
@click.option("--full", is_flag=True, default=False)
def list(remote=None, full=False):
    """List the available datasets

    Options:
        remote : The list to check, optional
        full : Flag, optionally prints out the remote location
    """

    from .. import datasets

    datasets.list_data(remote, full)


if __name__ == "__main__":
    cli()
