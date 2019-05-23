#!/usr/bin/env python
import numpy as np
import xarray
from . import common

def water(fname):
    """Calculate water column abundance in ice, vapor, h2oice"""

    variables = ["H2OICE", "QV_COLUMN", "QI_COLUMN"]
    data = dict()
    for v in variables:
        data.update(common.zonal_mean_surface(fname, v))
    
    return data
