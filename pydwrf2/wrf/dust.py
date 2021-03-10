import numpy as np
import xarray
import matplotlib.pyplot as plt
from ..plots import core
from ..datasets import load_data
import pandas as pd
import logging
from . import area_integrals

def process_file(fname, variable="TAU_OD2D", width=10, rescale=1.0):
    """Calculate the column optical depth over the equator."""

    nc = xarray.open_dataset(fname)
    dust = nc[variable]
    psfc = nc["PSFC"]
    area, y = area_integrals.read_area(nc)
    
    ls = nc["L_S"][:]
    times = nc["Times"][:]
    lats = nc["XLAT"].isel(Time=0,west_east=0)
    south_lim = np.where(lats<=-width)[0].max()
    north_lim = np.where(lats>+width)[0].min()
    print(south_lim, north_lim)
    
    tau_od2d = area_integrals.areasum(dust, area, south_lim=south_lim, north_lim=north_lim, mean=True)

    dust_scaled = area_integrals.areasum(610*dust/psfc, area, south_lim=south_lim, north_lim=north_lim,mean=True)
    dust_scaled /= rescale

    data =  dict(
        Times=times.load(),
        L_S=ls.load(),
        TAU_OD2D=tau_od2d.load(),
        taudust_scaled=dust_scaled.load()
    )

    nc.close()
    return xarray.Dataset(data)

def plot_dust_scaled(dust_filenames, output_filename, labels="", observation=True):

    fig = plt.figure(figsize=(8,6))
    ax = fig.gca()
    filename_list = [x for x in dust_filenames.split(",") if len(x)]
    labels_list = [x for x in labels.split(",") if len(x)]

    if len(labels_list) < len(filename_list):
        labels_list.extend(filename_list[len(labels_list):])

    limits = np.array([np.nan,np.nan,np.nan,np.nan])
            
    for label,filename in zip(labels_list, filename_list):
        with xarray.open_dataset(filename) as nc:
            h, mylimits = core.plotline(nc["L_S"], nc["taudust_scaled"],True, label=label)
            limits = core.replace_limits(limits, mylimits)
            
    if observation:
        logging.info("Plotting observations")
        # download the observation
        try:
            package = load_data("MikeSmithTES")
            for k,v in package.items():
                if v["status"] and k.count("obs/data/MikeSmithTES/MST.equatorial.csv"):
                    # read the observation
                    df = pd.read_csv(v["location"], comment="#")
                    # plot the observation
                    h, mylimits = core.plotline(df["L_S"],
                                                df["taudust_scaled"],
                                                True,
                                                label="TES dust opacity",
                                                alpha=0.8,
                                                color='grey')
                    
                    limits = core.replace_limits(limits, mylimits)
        except NameError as e:
            print(e)
            print("dust observation not found")
    
    plt.xlabel("L_S")
    plt.ylabel("Equatorial Dust opacity")
    plt.legend()
    plt.xticks(np.arange((limits[0]//180)*180, 180*(limits[1]//180)+180,180))

    plt.savefig(output_filename)


