import numpy as np
import xarray
from ..core import variables, utils


def _index(directory, output_filename):
    import glob
    if directory is None:
        pathjoin = lambda x,y : y
    else:
        pathjoin = lambda x, y: os.path.join(x,y)
    
    wrfout = glob.glob(pathjoin(directory, "wrfout*"))
    wrfrst = glob.glob(pathjoin(directory, "wrfrst*"))
    auxhist5 = glob.glob(pathjoin(directory, "auxhist5*"))
    auxhist8 = glob.glob(pathjoin(directory, "auxhist8*"))
    auxhist9 = glob.glob(pathjoin(directory, "auxhist9*"))

    files = dict(
        wrfout=sorted(wrfout),
        wrfrst=sorted(wrfrst),
        auxhist5=sorted(auxhist5),
        auxhist8=sorted(auxhist8),
        auxhist9=sorted(auxhist9),
    )

    import json

    json.dump(files, open(output_filename, "w"),indent=2)
    return files

def coord_match():
    data = dict(south_north="XLAT",
                west_east="XLONG",
                south_north_stag="XLAT_V",
                west_east_stag="XLONG_V")
    names = dict(south_north="Latitude",
                west_east="Longitude",
                south_north_stag="Latitude_stag",
                west_east_stag="Longitude_stag",
                XLAT="Latitude",
                XLONG="Longitude",
                XLAT_V="Latitude_stag",
                XLONG_V="Longitude_stag"
    )
    return data, names
         

def adjust_coords(data):
    coord, names = coord_match()
#    data = data.rename(dict((n,names[n]) for n in data.dims if n in names.keys()))
    return data
    
def zonal_mean_surface(fname, variable, rows=None):
    """Calculate the zonal mean value of a surface variable."""

    #close_file = False
    #if isinstance(fname,str):
    #    nc = xarray.open_dataset(fname)
    #    close_file = True
    #else:
    #    nc = fname
    data_dict = dict()
    with utils.open_dataset(fname) as nc:
        try:
            if variable not in nc:
                ex_filename = "unknown" if not isinstance(fname,str) else fname
                raise Exception ("Variable {} not found in file {}".format(variable, ex_filename))
            data = nc[variable]
            if "west_east" in data.dims:
                data_zonal_mean = data.mean("west_east")
            elif "west_east_stag" in data.dims:
                print("This average over west_east_stag' for variable {} is incorrect".format(variable))
                data_zonal_mean = data.mean("west_east")
    

    #        coord, names = coord_match()
            
            data_dict.update(dict((n,nc[n][:]) for n in ["L_S","Times"]))
            #data_dict.update(dict((n,nc[n].mean("west_east")) for n in ["XLAT"]))
            #Why do I have to take the mean of the data here instead of selecting one slice?
            data_dict["XLAT"] =nc["XLAT"].mean("west_east")
            data_dict[variable] = adjust_coords(data_zonal_mean)
    
        except Exception as e:
            #print("An Exception was raised: {}".format(e))
            #data = None
            raise(e)
        finally:
            
    #        if close_file:
#                nc.close()
            return data_dict
        
        
    

    

        
