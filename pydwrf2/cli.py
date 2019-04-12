import click
import logging
import os
import xarray

from .core import utils as cu


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug):
    logging.basicConfig(filename="pydwrf2.log", level=logging.INFO)
    pass  # click.echo("Debug mode is %s" % ("on" if debug else "off"))


@cli.command()
@click.argument("filename")
def calculate_t15(filename):
    logging.info("Calculate T15")


@cli.command()
@click.argument("filename")
def ls(filename):
    """Program to write the Ls data to the output file
        Args:
            filenames: wrfout files to process
        Returns:
            None
        Output:
            Ls and Times data in output file
    """
    logging.info("Ls")

    output_filename = cu.add_prefix_to_filename(filename, "ls.")
    logging.info(output_filename)

    with xarray.open_dataset(filename) as input:
        data = input[["Times", "L_S"]]
        data.to_netcdf(output_filename)


@cli.command()
@click.argument("filename")
def t15(filename):
    """Program to calculate T15 brightness temperatures

        Args:
            filename: filename
        Returns:
            table of data
    """
    from .wrf import t15 as wt15

    logging.info("T15")
    output_filename = cu.add_prefix_to_filename(filename, "t15.")

    logging.info(output_filename)

    with xarray.open_dataset(filename) as input:
        data = input[["Times", "L_S"]]
        data.to_netcdf(output_filename)

        dt = wt15.process_file(filename)
        data = xarray.Dataset(dt)
        data.to_netcdf(output_filename)


@cli.command()
@click.argument("filename")
@click.option("--variable", default="CO2ICE")
def icemass(filename, variable):
    """Program to calculate icemass

        Args:
            filename: filename
        Returns:
            table of data
    """
    from .wrf import icemass as wicemass

    logging.info("icemass")
    output_filename = cu.add_prefix_to_filename(filename, "{}.mass.".format(variable))

    logging.info(output_filename)

    with xarray.open_dataset(filename) as input:
        data = input[["Times", "L_S"]]
        data.to_netcdf(output_filename)

        dt = wicemass.process_file(filename, icevariable=variable)
        data = xarray.Dataset(dt)
        data.to_netcdf(output_filename)

if __name__ == "__main__":
    cli()
