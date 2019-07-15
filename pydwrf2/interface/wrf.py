import click
import xarray


def get_mode(filename):
    """Determine the mode for this output filename.

    If the file exists -> 'a'
    else -> 'w'
    """
    mode=''
    if os.path.exists(filename):
        logging.debug("{} exists, setting mode to 'a'".format(filename))
        mode='a'
    else:
        logging.debug("{} does not exist, setting mode to 'w'".format(filename))
        mode='w'
    return mode

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

    with xarray.open_dataset(filename) as input:
        data = remove_contiguous(input[["Times", "L_S"]])
        data.to_netcdf(output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename))


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.option("--lander", multiple=True, default=['vl1','vl2','msl','mpf'])
def lander(filename, output_filename, lander):
    """Program to calculate surface pressure at lander sites."""
    from ..wrf import vl

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
@click.option("--width",default=10)
def eq_tau_od2d(filename, output_filename, width=10):
    """Program to calculate equatorial dust opacity"""
    from ..wrf import dust

    with xarray.open_dataset(filename) as input:
        tau = dust.process_file(filename, width=width)

        tau = remove_contiguous(tau)

        tau.to_netcdf(output_filename, unlimited_dims=['Time'],mode=get_mode(output_filename))

        
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
    from ..wrf import t15 as wt15
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
    from ..wrf import icemass as wicemass

    logging.info("icemass")
    logging.info(output_filename)
    dt = wicemass.process_file(filename, icevariable=variable)
    data = remove_contiguous(xarray.Dataset(dt))
    data.to_netcdf(output_filename, unlimited_dims=["Time"],mode='w')#get_mode(output_filename))



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
    from ..wrf import energy_balance as eb

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
        def force_loop(s):
            if isinstance(s,str):
                return [s]
            else:
                return s
        data = dict()
        for v in force_loop(variable):
            print(v)
            data.update( zms(input, v) )
        zm = remove_contiguous(xarray.Dataset(data))
        zm.to_netcdf(output_filename, unlimited_dims=["Time"],mode=get_mode(output_filename))

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.argument("variable")
def zonal_mean_surface(filename, output_filename, variable):
    _zonal_mean_surface(filename, output_filename, variable.split(","))

@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def tau_od2d(filename, output_filename):
    _zonal_mean_surface(filename, output_filename, "TAU_OD2D")


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def water_column(filename, output_filename):
    """Calculate water column abundance in ice, vapor, h2oice"""

    variables = ["H2OICE", "QV_COLUMN", "QI_COLUMN"]
    _zonal_mean_surface(filename, output_filename, variables)



@cli.command()
@click.argument("filename")
@click.argument("output_filename")
def spinupsurface(filename, output_filename):
    """Calculate a suite of surface diagnostics"""

    variables = ["H2OICE", "QV_COLUMN", "QI_COLUMN",
                 "TSK", "PSFC", "TAU_OD2D","TAU_CL2D",
                 "QV_COLUMN","QI_COLUMN"
    ]
    _zonal_mean_surface(filename, output_filename, variables)

if __name__=="__main__":
    cli()