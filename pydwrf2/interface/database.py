import click

@click.group()
def cli():
    """Generate climatological databases from WRF."""
    pass

@cli.command()
def test():
    print("test")

if __name__ == "__main__":
    cli()