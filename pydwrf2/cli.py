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
@click.argument("output_filename")
def ls(filename, output_filename):
    """Program to write the Ls data to the output file
        Args:
            filenames: wrfout files to process
        Returns:
            None
        Output:
            Ls and Times data in output file
    """
    logging.info("Ls")

    logging.info(output_filename)

    with xarray.open_dataset(filename) as input:
        data = input[["Times", "L_S"]]
        data.to_netcdf(output_filename,unlimited_dims=["Time"])


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def t15(filename, output_filename):
    """Program to calculate T15 brightness temperatures

        Args:
            filename: filename
        Returns:
            table of data
    """
    from .wrf import t15 as wt15

    logging.info("T15")

    logging.info(output_filename)

    with xarray.open_dataset(filename) as input:
        data = input[["Times", "L_S"]]
        data.to_netcdf(output_filename)

        dt = wt15.process_file(filename)
        data = xarray.Dataset(dt)
        data.to_netcdf(output_filename,unlimited_dims=["Time"])


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.option("--variable", default="CO2ICE")
def icemass(filename, output_filename, variable):
    """Program to calculate icemass

        Args:
            filename: filename
        Returns:
            table of data
    """
    from .wrf import icemass as wicemass

    logging.info("icemass")

    logging.info(output_filename)

    with xarray.open_dataset(filename) as input:
        data = input[["Times", "L_S"]]
        dt = wicemass.process_file(filename, icevariable=variable)
        data = xarray.Dataset(dt)
        data.to_netcdf(output_filename, unlimited_dims=["Time"])


@cli.command()
@click.argument("directory")
@click.argument("output_filename")
def index(directory, output_filename):
    import glob

    wrfout = glob.glob(os.path.join(directory, "wrfout*"))
    wrfrst = glob.glob(os.path.join(directory, "wrfrst*"))
    auxhist5 = glob.glob(os.path.join(directory, "auxhist5*"))
    auxhist8 = glob.glob(os.path.join(directory, "auxhist8*"))
    auxhist9 = glob.glob(os.path.join(directory, "auxhist9*"))

    files = dict(
        wrfout=sorted(wrfout),
        wrfrst=sorted(wrfrst),
        auxhist5=sorted(auxhist5),
        auxhist8=sorted(auxhist8),
        auxhist9=sorted(auxhist9),
    )

    import json

    json.dump(files, open(output_filename, "w"),indent=2)

if __name__ == "__main__":
    cli()
