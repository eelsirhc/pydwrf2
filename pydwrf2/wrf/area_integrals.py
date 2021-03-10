import xarray
import numpy as np

def areasum(data, area=None, south_lim=-90, north_lim=90, mean=False):

    filtered_data = data.where((data.south_north >= south_lim) & (data.south_north < north_lim))    
    if area is not None:
        filtered_area = area.where((area.south_north >= south_lim) & (area.south_north < north_lim))
    else:
        filtered_area = 1
    
    
    result = (filtered_data*filtered_area).sum(["south_north", "west_east"], skipna=True)
    if mean:
        if isinstance(filtered_area,int):
            result /= filtered_data.size
        else:
            result /= filtered_area.sum(["south_north", "west_east"], skipna=True)
    return result

def read_area(nc):
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

    y = nc["XLAT"][:]
    d2r = np.deg2rad
    area = nc.RADIUS * nc.RADIUS * d2r(dx) * d2r(dy) * np.cos(d2r(y))

    return area, y

                  
