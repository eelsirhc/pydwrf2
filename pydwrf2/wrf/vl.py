import xarray
import netCDF4
import sys
import numpy
import argparse

import numpy as np
import matplotlib.pyplot as plt
from ..plots import core
from ..datasets import load_data
import pandas as pd

def interp_to_site(lon, lat, data, tolat, tolon):
    """Interpolates a dataset to a single longitude and latitude point"""
    wlon = numpy.where((lon[:-1] <= tolon)&(lon[1:]>tolon))
    wlon = wlon[0][0]
    wlat = numpy.where((lat[:-1] <= tolat)&(lat[1:]>tolat))
    wlat = wlat[0][0]
    
    p = data[:,wlat:wlat+2,wlon:wlon+2]
    fx = (tolon-lon[wlon])/(lon[wlon+1]-lon[wlon])
    fy = (tolat-lat[wlat])/(lat[wlat+1]-lat[wlat])
    a = p[:,0,0]*(1-fx) + p[:,0,1]*fx
    b = p[:,1,0]*(1-fx) + p[:,1,1]*fx
    c = a*(1-fy) + b*fy

    return c
    
def func_pressure_curve(nc, index, loc, alldata=False):
    """Given the location dictionary (lon,lat, height), calculates
    the surface pressure at the location and adjust the value from the
    model surface height to the 'true' provided height"""

    index = index or slice(None,None)
    
    lon = numpy.squeeze(nc["XLONG"][0,0,:]).values
    lat = numpy.squeeze(nc["XLAT"][0,:,0]).values
    psfc = nc["PSFC"][index].values
    psfc_loc = interp_to_site(lon, lat, psfc, loc["lat"],loc["lon"])
    
    if "height" not in loc:
        return psfc_loc
    
    rd    = nc.R_D
    cp    = nc.CP
    grav  = nc.G
    tsfc = nc["TSK"][index]
    hgt = nc["HGT"][index]
    
    tsfc_loc = interp_to_site(lon, lat, tsfc, loc["lat"],loc["lon"])
    hgt_loc  = interp_to_site(lon, lat, hgt,  loc["lat"],loc["lon"])

    rho = psfc_loc/(rd*tsfc_loc)
    dp  = -rho*grav*(loc["height"]-hgt_loc)
    
    corrected_psfc = psfc_loc+dp
    if alldata:
      data = dict(psfc_uncorrected=psfc_loc, 
                  psfc_corrected=corrected_psfc,
                  hgt=hgt_loc,
                  tsfc=tsfc_loc,
                  dp=dp,
                  rho=rho)
    else:
#        print(psfc_loc.shape, psfc_loc)
#        psfc_loc = psfc_loc.rename(dict(XLAT="{}_XLAT".format(loc["prefix"])))
#        corrected_psfc = corrected_psfc.rename(dict(XLAT="{}_XLAT".format(loc["prefix"])))
#        tsfc_loc = tsfc_loc.rename(dict(XLAT="{}_XLAT".format(loc["prefix"])))
        data = dict(psfc_uncorrected=xarray.DataArray(psfc_loc,dims=("Time",)),
                    psfc_corrected=xarray.DataArray(corrected_psfc, dims=("Time",)),
                    tsfc=xarray.DataArray(tsfc_loc,dims=("Time",)))
    data = dict([("{}_{}".format(loc["prefix"],k),v) for k,v in data.items()])
    return data

def func_vl1_pressure_curve(nc, index=None):
    """Calculates the surface pressure at Viking Lander 1"""
    loc  = {"lat":22.2692, "lon":-48.1887, "height":-3627., "prefix": "vl1"}
    return func_pressure_curve(nc, index, loc)
    
def func_vl2_pressure_curve(nc, index=None):
    """Calculates the surface pressure at Viking Lander 2"""
    loc = {"lat": 47.6680, "lon": 134.0430, "height": -4505.0, "prefix": "vl2"}
    return func_pressure_curve(nc, index, loc)

def func_mpf_pressure_curve(nc, index=None):
    """Calculates the surface pressure at MPF"""
    loc = {"lat": 19.0949, "lon": -33.4908, "height": -3682.0, "prefix":"mpf"}
    return func_pressure_curve(nc, index, loc)

def func_msl_pressure_curve(nc,index=None):
    """MSL location, but not altitude!"""
    loc = {"lat": -4.5, "lon": 137.4, 'height': -4501., "prefix":"msl"}
    return func_pressure_curve(nc,index,loc)



def plot_single_lander(lander_filenames, labels, prefix, ax, observation=True):
    if len(labels) < len(lander_filenames):
        labels.extend(lander_filename[len(labels_list):])

    limits = np.array([np.nan,np.nan,np.nan,np.nan])
    for label,filename in zip(labels, lander_filenames):
        if label=="":
            label=filename
        with xarray.open_dataset(filename) as nc:
            ls, psfc = nc["L_S"], nc["{}_psfc_corrected".format(prefix)]
            if psfc.isel(Time=0)<=100:
                ls = ls.isel(Time=slice(1,None))
                psfc = psfc.isel(Time=slice(1,None))
            h, mylimits = core.plotline(ls, psfc, True, label=label, ax=ax)
            limits = core.replace_limits(limits, mylimits)
    ax.set_xlabel("L_S")
    ax.set_ylabel("Pressure (Pa)")
    ax.set_title(prefix)
    if observation:
        # download the observation
        try:
            package = load_data(prefix.upper())
            for k,v in package.items():
                if v["status"] and k.count(prefix):
                    # read the observation
                    df = pd.read_csv(v["location"], comment="#")
                    # plot the observation
                    h, mylimits = core.plotline(df["L_S"],
                                                df["psfc"],
                                                True,
                                                label="{}".format(prefix),
                                                alpha=0.8,
                                                color='grey',ax=ax)
                    
                    limits = core.replace_limits(limits, mylimits)
        except NameError as e:
            print(e)
            print("Surface pressure for {} not found.".format(prefix))

            
def plot_lander(lander_filenames, output_filename, labels="", observation=True, prefixes=None):
    #loop through the lander names and plot a figure for each one.

    #loop through lander names
    #each entry has prefix_psfc_uncorrected, prefix_psfc_corrected, prefix_tsfc

    prefixes = prefixes or ["vl1", "vl2", "msl", "mpf"]
    fig, axs = plt.subplots(2,2,figsize=(8,11))
    axs = axs.ravel()
    for ax,prefix in zip(axs,prefixes):
        plot_single_lander(lander_filenames, labels, prefix, ax, observation=observation)
        ax.legend()
    plt.tight_layout()
    plt.savefig(output_filename)
    
    
