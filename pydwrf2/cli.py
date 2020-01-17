import argh, argparse
import logging
from .core import utils as cu
from .interface import plot, database, data, single, wrf, snake


def cli(debug=False):
    """The master CLI interface."""
    import logging.config
    import yaml
    try:
        with open('config_log.yaml', 'r') as f:
          config = yaml.safe_load(f.read())
          logging.config.dictConfig(config)
          logger = logging.getLogger(__name__)
    except Exception as e:
      logging.basicConfig(filename="pydwrf2.log", level=logging.INFO)


def register(com, group, name=None, individual=False):
    """Helper function to register command groups.

    Args:
      com   : The object to register onto
      group : The group of commands to register, usually as a sub command
    Options:
      name : The alternate name of the command group
      individual :  Logical, if true, imports the commands in the
                    group individually.
    """

    # If the name is not given, use the default
    if name is not None:
        name = group["name"]

    # If not adding individual, add the entire group in one go
    if not individual:
        logging.info("Adding group {} with name".format(group, name))
        argh.add_commands(com, group["commands"], namespace=name)
        #com.add_command(group)
    else:
        # add each entry in the group defined.
        for key, entry in group.commands.items():
            com.add_command(entry)



def main():
    SUBCOMMANDS = dict(
    plot=plot.cli,
#    database=database.cli,
#    data=data.cli,
#    single=single.cli,
#    wrf=wrf.cli,
#    snake=snake.cli,
)

    parser = argparse.ArgumentParser()
    argh.add_commands(parser, [cli])

    INDIVIDUAL = dict(single=True)
    for k, v in SUBCOMMANDS.items():
      register(parser, v, name=k, individual=INDIVIDUAL.get(k, False))
    argh.dispatch(parser)

if __name__ == "__main__":
    main()
