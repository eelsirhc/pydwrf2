import click
from .common import LazyGroup


@click.group()#(cls=LazyGroup, import_name='pydwrf2.database:cli')
def cli():
    """Generate climatological databases from WRF."""
    pass

@cli.command()
def test():
    print("test")

@click.group()
def database():
    pass

def csv(s):
    return s.split(",")
    
@cli.command()
@click.argument("variable")
@click.argument("index_filename")
@click.argument("output_filename")
@click.option("--aggregation", type=csv, default="mean,std")
def aggregate(variable, index_filename, output_filename, aggregation):
    """Dumb average of data"""
    from ..database import commands
    commands.aggregate(variable, index_filename, output_filename, aggregation)


@cli.command()
@click.argument("low", type=float)
@click.argument("high", type=float)
@click.option(
    "--database_filename", type=str, default="output/database/database_index.csv"
)
@click.option("--database_ls_prefix", type=str, default="output/database/database-ls")
@click.option("--partial_sol", is_flag=True, default=False)
@click.option("--format_string", default="05.1f")
def index_ls(low, high,
    database_filename="output/database/database_index.csv",
    database_ls_prefix="output/database/database-ls",
    partial_sol=True,
    format_string="05.1f"):
    """Create an L_S specfic index.

    This file acts as a gateway to remaking a database file.
    """
    from ..database import commands
    commands.index_ls(low, high,
    database_filename=database_filename,
    database_ls_prefix=database_ls_prefix,
    partial_sol=partial_sol,
    format_string=format_string)    


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def index_one_file(filename, output_filename):
    from ..database import commands
    commands.index_one_file(filename, output_filename)

    
@cli.command()
@click.option("--index_filename", type=str, default="output/index")
@click.option(
    "--database_filename", type=str, default="output/database/database_index.csv"
)
@click.option(
    "--intermediate", type=str, default="output/intermediate"
)
def index(index_filename="output/index",
    database_filename="output/database/database_index.csv",
    intermediate="output/intermediate"):
    """Create a new index file for the database.

    Each line includes an index number into each file from the entire wrfout collection
    and the L_S and local time of that index."""
    from ..database import commands
    commands.index(index_filename=index_filename,
        database_filename=database_filename,
        intermediate=intermediate)

if __name__ == "__main__":
    cli()


