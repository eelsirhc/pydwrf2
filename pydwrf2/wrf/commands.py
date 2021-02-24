"""Commands for the wrf model."""

import os
import logging
import xarray
import numpy as np
from .common import get_mode, remove_contiguous, add_attributes

def eq_tau_od2d(filename, output_filename, width=10):
    """Function to calculate zonal mean equatorial dust opacity.


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


def zonal_mean_surface(filename, output_filename, variable, attributes=None):
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
            logging.debug("Calculating {}".format(v))
            data.update(zms(input, v))
        zm = remove_contiguous(xarray.Dataset(data))

        add_attributes(zm,attributes)
        zm.to_netcdf(
            output_filename, unlimited_dims=["Time"], mode=get_mode(output_filename)
        )
