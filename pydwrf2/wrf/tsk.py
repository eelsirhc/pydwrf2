import numpy as np
import xarray
import matplotlib.pyplot as plt
from ..plots import core
from ..datasets import load_data
import pandas as pd
import logging
from . import area_integrals

def process_file(fname, variable="TSK", width=10):
    """Calculate the surface temperature over the equator."""

    nc = xarray.open_dataset(fname)
    tsk_raw = nc[variable]
    area, y = area_integrals.read_area(nc)
    
    ls = nc["L_S"][:]
    times = nc["Times"][:]

    lats = nc["XLAT"].isel(Time=0,west_east=0)
    south_lim = np.where(lats<=-width)[0].max()
    north_lim = np.where(lats>=+width)[0].min()
    
    tsk = area_integrals.areasum(tsk_raw, area, south_lim=south_lim, north_lim=north_lim, mean=True)

    data =  dict(
        Times=times.load(),
        L_S=ls.load(),
        TSK=tsk.load(),
    )

    nc.close()
    return xarray.Dataset(data)
