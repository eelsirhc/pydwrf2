import xarray
import numpy as np
from ..core import variables

def pressure(nc):
    """Returns the full pressure."""

    if "PRES" in nc:
        press = nc["PRES"]
    else:
        press = nc["P"] + nc["PB"] #Hopefully, dask will step in and delay a calculation until it's needed.

    return press

def temperature(nc):
    """Returns the full temperature."""

    if "TEMP" in nc:
        temp = nc["TEMP"]
    else:
        pres = pressure(nc)
        temp = (nc["THETA"] + nc.T0)*(pres/nc.P0)**(nc.R_D/nc.CP)

    return temp
