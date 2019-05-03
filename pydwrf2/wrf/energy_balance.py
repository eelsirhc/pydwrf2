#!/usr/bin/env python
import numpy as np
import xarray
from tqdm import tqdm
from ..core import variables
import logging

def process_file(fname):
    """Calculate the total energy input into the atmosphere as a function of time."""

    nc = xarray.open_dataset(fname)
    nc['area'] = variables.area(nc)
    sigma = 5.67e-8
    nc["UPFLUX"] = nc["TSK"]**4 * sigma 
    simple_energy_inputs = dict(TOASW=+1,
                                TOALW=-1,
                                RNET_2D=-1,
                                HFX=+1)

    def areasum(data, area):
        return (data * area).sum(["south_north", "west_east"], skipna=True)

    data = dict()
    datasum = 0

    for varname in simple_energy_inputs.keys():
        logging.info(varname)
        if varname in nc:
            data[varname] = simple_energy_inputs[varname] * areasum(nc[varname],nc['area'])
            datasum = datasum + data[varname]
        else:
            print("{} not in nc".format(varname))

    if "GSW" in nc:
        logging.info("GSW")
        data["GSW"] = -areasum(nc["GSW"],nc["area"])
    if "GLW" in nc and "EMISS" in nc:
        logging.info("GLW")
        data["GLW"] = -areasum(nc["GLW"]*nc["EMISS"],nc["area"])
    if "UPFLUX" in nc and "EMISS" in nc:
        logging.info("UPFLUX")
        data["UPFLUX"] = areasum(nc["UPFLUX"]*nc["EMISS"],nc["area"])

    data["SWDOWN"] = areasum(nc["SWDOWN"],nc["area"])
    
    sw_down_absorbed_fraction = 1 - (nc["TOASW"]-nc["SWDOWN"])/nc["TOASW"]
    sw_up_not_absorbed = - (nc["SWDOWN"] - nc["GSW"]) * (nc["SWDOWN"]/nc["TOASW"])
    logging.warning("faking the swout")
    data["fake_swout"] = areasum(sw_up_not_absorbed, nc["area"])
    logging.warning("Hard coded co2 latent heat")
    co2_lheat = 5.713e5
    cond = -areasum(nc["CO2ICE"],nc["area"])
    dcond = cond.diff("Time")*co2_lheat
    cond[1:] = dcond
    logging.warning("hard coded time interval")
    data["CO2"] = cond/(14400*60)
    data["area"] = areasum(1,nc["area"])**2
    
    compounds = dict(eb_lw = ["GLW","UPFLUX","TOALW"],
                     eb_sw = ["GSW","TOASW","fake_swout"],
                     eb_thermal = ["HFX","CO2"],
                     eb_toa = ["TOASW","TOALW","fake_swout"],
                     eb_surface =["RNET_2D","HFX","CO2"],
                     eb_sum = ["RNET_2D","HFX","TOASW","TOALW","fake_swout","CO2"])

    for key,var in compounds.items():
        logging.info(key)
        data[key] = 0
        for k in var:
            if k in data:
                data[key]+=data[k]
    

    for k in data.keys():
        data[k]/=areasum(1,nc["area"])
    
    data.update(dict(times=nc["Times"],ls=nc["L_S"]))
    return data

    
