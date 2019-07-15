#import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as mpl_cm
import palettable.colorbrewer as cb
from .scaled_ticks import ScaledLocator, ScaledFormatter, LsFormatter
from ..core import variables
import numpy as np
import json
from os.path import dirname,join

def replace_limits(old,new):
    old = np.where(np.isnan(old), new,old)
    low = slice(None,None,2)
    high = slice(1,None,2)
    old[low] = np.where(old[low]>new[low],new[low],old[low])
    old[high] = np.where(old[high]<new[high],new[high], old[high])
    return old


def get_map(cmap):
    """Get a color map based on the name.
    """
    try:
        if isinstance(cmap,str):
            colormaps=dict(spectral=Spectral_11_r,
                           bluered=RdBu_11_r
                           )
            return colormaps[cmap]
        elif isinstance(cmap,list):
            return cb.get_map(*cmap)
        else:
            return Spectral_11_r
    except Exception as e:
        print("Colormap {0} failed: {1}".format(cmap,e))
        return Spectral_11_r


def plotline(x, data, continuous_ls=False, ax=None,*args, **kwargs):
    if continuous_ls:
        x = variables.continuous_ls(x)
    if ax is None:
        ax = plt.gca()
    h = ax.plot(x, data, *args, **kwargs)
    limits = np.array([np.nanmin(x), np.nanmax(x), np.nanmin(data), np.nanmax(data)])
    return h, limits

class Configuration(object):
    def __init__(self, filename=None):
        if filename is None:
            module_path = dirname(__file__)
            filename = join(module_path, "wrf_levels.json")
        self.filename = filename

        self.data = json.load(open(filename))
        self.defaults = dict(cmap="viridis")
        
    def _arange(self, alevels):
        levels = []
        for c in alevels:
            if isinstance(c,list):
                levels.append(np.arange(*c))
            else:
                levels.append(c)
        return np.hstack(levels)
        
    def level(self, variable, dimension=2):
        levels = None
        if variable in self.data:
            if "levels" in self.data[variable]:
                levels = self.data[variable]["levels"]
            elif "alevels" in self.data[variable]:
                levels = self._arange(self.data[variable]["alevels"])
            return levels

    def __contains__(self, variable):
        return variable in self.data

    def _fill_defaults(self,variable):
        d=self.defaults.copy()
        for k,v in self.defaults.items():
            if k in self.data[variable]:
                d[k] = self.data[variable][k]
        return d
        
    def options(self,variable):
        options = dict()
        if variable in self.data:
            #levels
            options["levels"] = self.level(variable)
            #defaults
            options.update(self._fill_defaults(variable))
                
        options = dict((k,v) for k,v in options.items() if v is not None)
        return options
