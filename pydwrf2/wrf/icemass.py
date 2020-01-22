#!/usr/bin/env python
import numpy as np
import xarray
import matplotlib.pyplot as plt
from ..plots import core
from ..datasets import load_data
import pandas as pd
from . import area_integrals
import logging

def process_file(fname, icevariable="CO2ICE", rows=None):
    """Calculate the area total icemass for the named ice variable."""

    nc = xarray.open_dataset(fname)
    area, y = area_integrals.read_area(nc)

    co2ice = nc[icevariable]

    ls = nc["L_S"][:]
    times = nc["Times"][:]
    mu = nc["MU"] + nc["MUB"]
    
    equator = co2ice.south_north[co2ice.XLAT.sel(Time=0, west_east=0) > 0].min()
    
    nh_icemass = area_integrals.areasum(co2ice, area, south_lim=equator)
    sh_icemass = area_integrals.areasum(co2ice, area, north_lim=equator)
    icemass = area_integrals.areasum(co2ice, area)
    airmass = area_integrals.areasum(mu,area)
    
    data =  dict(
        Times=times.load(),
        L_S=ls.load(),
        icemass=icemass.load(),
        nh_icemass=nh_icemass.load(),
        sh_icemass=sh_icemass.load(),
        airmass=airmass.load()
    )
    nc.close()
    return data
