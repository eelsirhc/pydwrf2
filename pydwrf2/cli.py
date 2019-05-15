import click
import logging
import os
import xarray

from .core import utils as cu

def get_mode(filename):
    """Determine the mode for this output filename.

    If the file exists -> 'a'
    else -> 'w'
    """
    if os.path.exists(filename):
        logging.debug("{} exists, setting mode to 'a'".format(filename))
        return 'a'
    else:
        logging.debug("{} does not exist, setting mode to 'w'".format(filename))
        return 'w'


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
        data = remove_contiguous(input[["Times", "L_S"]])
        data.to_netcdf(output_filename,unlimited_dims=["Time"],mode=get_mode(output_filename))

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.option("--lander", multiple=True, default=['vl1','vl2','msl','mpf'])
def lander(filename, output_filename, lander):
    """Program to calculate surface pressure at lander sites."""
    from .wrf import vl

    functions=dict(vl1=vl.func_vl1_pressure_curve,
                   vl2=vl.func_vl2_pressure_curve,
                   mpf=vl.func_mpf_pressure_curve,
                   msl=vl.func_msl_pressure_curve)

    with xarray.open_dataset(filename) as input:
        pressure = [xarray.Dataset(functions[k](input,None)) for k in lander]
        pressure = xarray.merge(pressure)
        pressure["L_S"] = input["L_S"]
        pressure["Times"] = input["Times"]
        pressure = remove_contiguous(pressure)

        pressure.to_netcdf(output_filename, unlimited_dims=['Time'],mode=get_mode(output_filename))
        
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
        dt = wt15.process_file(filename)
        data = xarray.Dataset(dt)
        data["L_S"] = input["L_S"]
        data["Times"] = input["Times"]
        data = remove_contiguous(data)
        
        data.to_netcdf(output_filename,unlimited_dims=["Time"],mode=get_mode(output_filename))


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
        data = remove_contiguous(xarray.Dataset(dt))
        data.to_netcdf(output_filename, unlimited_dims=["Time"],mode=get_mode(output_filename))



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
    from .wrf import energy_balance as eb

    logging.info("energy balance")

    logging.info(output_filename)

    with xarray.open_dataset(filename) as input:
#        data = input[["Times", "L_S"]]
        dt = eb.process_file(filename)
        data = remove_contiguous(xarray.Dataset(dt))
        data.to_netcdf(output_filename, unlimited_dims=["Time"],mode=get_mode(output_filename))

def _zonal_mean_surface(filename, output_filename, variable):
    from .wrf.common import zonal_mean_surface as zms
    logging.info("zonal mean for {}".format(variable))
    logging.info("output to {}".format(output_filename))

    with xarray.open_dataset(filename) as input:

        zm = xarray.Dataset(
            zms(input, variable)
            )
        zm["L_S"] = input["L_S"]
        zm["Times"] = input["Times"]
        zm = remove_contiguous(zm)

        zm.to_netcdf(output_filename, unlimited_dims=["Time"],mode=get_mode(output_filename))

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.argument("variable")
def zonal_mean_surface(filename, output_filename, variable):
    _zonal_mean_surface(filename, output_filename, variable)

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def tau_od2d(filename, output_filename):
    _zonal_mean_surface(filename, output_filename, "TAU_OD2D")



        
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

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.argument("variable")
def quickplot(filename, output_filename, variable):
    from . import plots as wplot
    wplot.quick_plot(filename, output_filename, variable)

if __name__ == "__main__":
    cli()
