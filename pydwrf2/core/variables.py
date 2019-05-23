import xarray
import numpy as np

def either(*args):
    def access(nc):
        for k in args:
            if k in nc.variables:
                return nc[k]
        raise NameError("Names not found: {}".format(",".join(args)))
    return access

def latitude(nc):
    lat = either("Latitude","XLAT")(nc)
    if "Time" in lat.dims:
        lat=lat.isel(Time=0)
    return lat
    
    
def slice_ls(ls, threshold=-100):
    w = np.where(np.diff(ls)< threshold)
    if len(w)==0:
        slices = [slice(0,len(ls))]
    else:
        sl = np.hstack([-1,w[0],ls.size-1])
        slices = [slice(a+1,b+1) for a,b in zip(sl[:-1],sl[1:])]
    return slices
    
def continuous_ls(ls, threshold=-100):
    """Converts Ls into a continuous monotic variable."""

    return np.hstack([i*360+ls[s] for i,s in enumerate(slice_ls(ls, threshold))])
    
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
