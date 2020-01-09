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

def plot_icemass(ice_filenames, output_filename, labels="", observation=True, wrap=False):
    fig = plt.figure(figsize=(8,6))
    ax = fig.gca()
    filename_list = [x for x in ice_filenames.split(",") if len(x)]
    labels_list = [x for x in labels.split(",") if len(x)]

    if len(labels_list) < len(filename_list):
        labels_list.extend(filename_list[len(labels_list):])

    limits = np.array([np.nan,np.nan,np.nan,np.nan])
    
    wrap_func = lambda x: x
    if wrap:
        wrap_func = lambda x: x%360
    for label,filename in zip(labels_list, filename_list):
        with xarray.open_dataset(filename) as nc:
            for ls,suffix in zip(["-",":","--"],["","nh_","sh_"]):
                h, mylimits = core.plotline(wrap_func(nc["L_S"]), nc["{}icemass".format(suffix)],True, label=label+" "+suffix.strip("_"),ls=ls)
                limits = core.replace_limits(limits, mylimits)
            
    if observation:
        logging.info("Plotting observation")
        # download the observation
        try:
            package = load_data("GRS")
            for k,v in package.items():
                if v["status"] and k.count("grs"):
                    # read the observation
                    table = pd.read_csv(v["location"], comment="#")
                    # plot the observation
                    for ls,suffix in zip(["-",":","--"],["total_","nh_","sh_"]):
                        h, mylimits = core.plotline(wrap_func(table["L_S"]),
                                                    table["{}icemass".format(suffix)],
                                                    True,
                                                    label="grs "+suffix.strip("_"),
                                                    ls=ls,
                                                    alpha=0.8,
                                                    color='grey')
                        
                        limits = core.replace_limits(limits, mylimits)
        except NameError as e:
            print(e)
            print("icemass observation not found")

    plt.xlabel("L_S")
    plt.ylabel("Ice mass (kg)")
    plt.legend()
        
    plt.savefig(output_filename)

