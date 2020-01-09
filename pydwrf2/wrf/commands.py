"""Commands for the wrf model."""

import os
import logging
import xarray
import numpy as np


def remove_contiguous(data, entry="contiguous"):
    """Removes the contiguous entry from the encoding from certain variables.
      Args:
        data  : object, probably xarray, containing 'variables'
        entry : a string to search for and remove.
      Remove:
        data : cleaned.
    """
    for var in data.variables:
        if entry in data[var].encoding:
            del data[var].encoding[entry]
    return data


def get_mode(filename):
    """Determine the mode for this output filename.

    If the file exists -> 'a' (append)
    else -> 'w' (write)
    """
    mode = ""
    if os.path.exists(filename):
        logging.debug("{} exists, setting mode to 'a'".format(filename))
        mode = "a"
    else:
        logging.debug("{} does not exist, setting mode to 'w'".format(filename))
        mode = "w"
    return mode


def ls(filename, output_filename):
    """Function to write the Ls data to the output file
        Args:
            filenames: wrfout files to process
        Returns:
            None
        Output:
            Ls and Times data in output file
    """
    with xarray.open_dataset(filename) as input:
        logging.info("Calculating")
        data = remove_contiguous(input[["Times", "L_S"]])
        logging.info("Saving")
        data.to_netcdf(
            output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename)
        )


def lander(filename, output_filename, lander):
    """Function to calculate surface pressure at lander sites.

    Calls internal code to interpolate data to the correct location
    and adjust hydrostatically.

    Args:
        filename: wrfout file to process
        output_filename : The output filename
        lander : list of lander names
    Returns:
        None
    Output:
        Lander pressure and Ls in the output file
    """
    from . import vl

    functions = dict(
        vl1=vl.func_vl1_pressure_curve,
        vl2=vl.func_vl2_pressure_curve,
        mpf=vl.func_mpf_pressure_curve,
        msl=vl.func_msl_pressure_curve,
    )

    with xarray.open_dataset(filename) as input:
        logging.info("Calculating")
        pressure = [xarray.Dataset(functions[k](input, None)) for k in lander]
        pressure = xarray.merge(pressure)
        pressure["L_S"] = input["L_S"]
        pressure["Times"] = input["Times"]
        pressure = remove_contiguous(pressure)
        logging.info("Saving")
        pressure.to_netcdf(
            output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename)
        )


def eq_tau_od2d(filename, output_filename, width=10):
    """Function to calculate equatorial dust opacity.


    Args:
        filename: wrfout file to process
        output_filename : The output filename
        width : [10] latitudinal width centered on the equator.
    Returns:
        None
    Output:
        Dust opacity from tau_od2d and Ls in the output file
    """
    from . import dust

    with xarray.open_dataset(filename) as input:
        logging.info("Calculating")
        tau = dust.process_file(filename, width=width)
        tau = remove_contiguous(tau)
        logging.info("Saving")
        tau.to_netcdf(
            output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename)
        )


def t15(filename, output_filename):
    """Program to calculate T15 brightness temperatures

        Args:
            filename: filename
        Returns:
            table of data
    """
    from . import t15 as wt15

    with xarray.open_dataset(filename) as input:
        logging.info("Calculating")
        dt = wt15.process_file(filename)
        data = xarray.Dataset(dt)
        data[" L_S"] = input["L_S"]
        data["Times"] = input["Times"]
        data = remove_contiguous(data)
        logging.info("Saving")
        data.to_netcdf(
            output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename)
        )


def icemass(filename, output_filename, variable="CO2ICE"):
    """Program to calculate icemass

        Args:
            filename: filename
        Returns:
            table of data
    """
    from . import icemass as wicemass
    logging.info("Calculating")
    table = wicemass.process_file(filename, icevariable=variable)
    data = remove_contiguous(xarray.Dataset(table))
    logging.info("Saving")
    data.to_netcdf(
        output_filename, unlimited_dims=["Time"], mode="w"
    )


def energy_balance(filename, output_filename):
    """Program to calculate energy balance

        Args:
            filename: filename
        Returns:
            table of data
    """
    from . import energy_balance as eb

    with xarray.open_dataset(filename) as input_data:
        logging.info("Calculating")
        table = eb.process_file(filename)
        data = remove_contiguous(xarray.Dataset(table))
        logging.info("Saving")
        data.to_netcdf(
            output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename)
        )


def zonal_mean_surface(filename, output_filename, variable):
    from .common import zonal_mean_surface as zms

    logging.info("zonal mean for {}".format(variable))
    logging.info("output to {}".format(output_filename))

    with xarray.open_dataset(filename) as input:

        def force_loop(s):
            if isinstance(s, str):
                return [s]
            else:
                return s

        data = dict()
        for v in force_loop(variable):
            print(v)
            data.update(zms(input, v))
        zm = remove_contiguous(xarray.Dataset(data))
        zm.to_netcdf(
            output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename)
        )
