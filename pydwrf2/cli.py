import click
import logging

from .core import utils as cu


def remove_contiguous(data, entry="contiguous"):
    for var in data.variables:
        if entry in data[var].encoding:
            del data[var].encoding[entry]
    return data


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    logging.basicConfig(filename="pydwrf2.log", level=logging.INFO)
    pass  # click.echo("Debug mode is %s" % ("on" if debug else "off"))


from .interface import plot, database, data, single, wrf, snake

def register(com, group, name=None, individual=False):
    if name is not None:
        group.name = name
    if not individual:
        logging.info("Adding group {} with name".format(group, group.name))
        com.add_command(group)
    else:
        for ke, entry in group.commands.items():
            com.add_command(entry)

subcommands = dict(plot=plot.cli,
                   database=database.cli,
                   data=data.cli,
                   single=single.cli,
                   wrf=wrf.cli,
                   snake=snake.cli)

individual = dict(single=True)
for k, v in subcommands.items():
    register(cli, v, name=k, individual=individual.get(k,False))



if __name__ == "__main__":
    cli()
