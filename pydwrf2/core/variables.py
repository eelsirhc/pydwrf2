import xarray
import numpy as np

def area(nc):
    if "XLAT_V" in nc:
        dy = (
            nc["XLAT_V"][:]
            .diff("south_north_stag")
            .rename(dict(south_north_stag="south_north"))
        )
    else:
        dy = nc["XLAT_V"][:].diff("south_north").mean()

    if "XLONG_U" in nc:
        dx = nc["XLONG_U"][:].diff("west_east_stag").rename(dict(west_east_stag="west_east"))
    else:
        dx = nc["XLONG_U"][:].diff("west_east").mean()

    y = nc["XLAT"]
    d2r = np.deg2rad
    area = nc.RADIUS * nc.RADIUS * d2r(dx) * d2r(dy) * np.cos(d2r(y))
    return area
