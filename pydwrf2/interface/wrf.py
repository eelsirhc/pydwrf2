import click
import logging
from ..wrf import commands

@click.group()
def cli():
    """Calculate diagnostics from WRF output files."""
    pass


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
    
    commands.ls(filename, output_filename)

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.option("--lander", multiple=True, default=["vl1", "vl2", "msl", "mpf"])
def lander(filename, output_filename, lander):
    """Program to calculate surface pressure at lander sites."""
    logging.info("Lander")
    logging.info("Landers: {}".format(",".join(lander)))
    logging.info(filename)
    logging.info(output_filename)
    commands.lander(filename, output_filename, lander)


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.option("--width", default=10)
def eq_tau_od2d(filename, output_filename, width=10):
    """Program to calculate zonal mean equatorial dust opacity"""
    logging.info("Dust")
    logging.info("Width: {}".format(width))
    logging.info(filename)
    logging.info(output_filename)
    commands.eq_tau_od2d(filename, output_filename, width=width)


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def t15(filename, output_filename):
    """Program to calculate T15 brightness temperatures
    """

    logging.info("T15")
    logging.info(filename)
    logging.info(output_filename)
    commands.t15(filename, output_filename)

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
    logging.info("icemass")
    logging.info(filename)
    logging.info(output_filename)
    logging.info(variable)
    commands.icemass(filename, output_filename, variable)

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def energy_balance(filename, output_filename):
    """Program to calculate energy balance

        Args:
            filename: filename
        Returns:
            table of data
    """
    logging.info("energy balance")
    logging.info(filename)
    logging.info(output_filename)
    commands.energy_balance(filename, output_filename)


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.argument("variable")
def zonal_mean_surface(filename, output_filename, variable):
    commands.zonal_mean_surface(filename, output_filename, variable.split(","))


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def tau_od2d(filename, output_filename):
    commands.zonal_mean_surface(filename, output_filename, "TAU_OD2D")


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def water_column(filename, output_filename):
    """Calculate water column abundance in ice, vapor, h2oice"""

    variables = ["H2OICE", "QV_COLUMN", "QI_COLUMN"]
    commands.zonal_mean_surface(filename, output_filename, variables)


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def spinupsurface(filename, output_filename):
    """Calculate a suite of surface diagnostics"""

    variables = [
        "H2OICE",
        "QV_COLUMN",
        "QI_COLUMN",
        "TSK",
        "PSFC",
        "TAU_OD2D",
        "TAU_CL2D",
        "QV_COLUMN",
        "QI_COLUMN",
    ]
    commands.zonal_mean_surface(filename, output_filename, variables)


if __name__ == "__main__":
    cli()
