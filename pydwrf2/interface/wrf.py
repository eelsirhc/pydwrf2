import click
import logging
from .common import LazyGroup

@click.group()#(cls=LazyGroup, import_name="pydwrf2.cli:wrf")
def cli():
    """Calculate diagnostics from WRF output files."""
    pass


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
    from ..wrf import commands
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
    from ..wrf import commands
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
    from ..wrf import commands
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
    from ..wrf import commands
    commands.energy_balance(filename, output_filename)


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.argument("variable")
def zonal_mean_surface(filename, output_filename, variable):
    logging.info("zonal mean surface")
    logging.info(filename)
    logging.info(output_filename)
    from ..wrf import commands
    commands.zonal_mean_surface(filename, output_filename, variable.split(","))


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def tau_od2d(filename, output_filename):
    logging.info("tau_od2d")
    logging.info(filename)
    logging.info(output_filename)
    from ..wrf import commands
    commands.zonal_mean_surface(filename, output_filename, "TAU_OD2D")


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def water_column(filename, output_filename):
    """Calculate water column abundance in ice, vapor, h2oice"""
    logging.info("water column")
    logging.info(filename)
    logging.info(output_filename)
    from ..wrf import commands
    variables = ["H2OICE", "QV_COLUMN", "QI_COLUMN"]
    commands.zonal_mean_surface(filename, output_filename, variables)


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def spinupsurface(filename, output_filename):
    """Calculate a suite of surface diagnostics"""
    logging.info("spinup surface")
    logging.info(filename)
    logging.info(output_filename)
    from ..wrf import commands
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
