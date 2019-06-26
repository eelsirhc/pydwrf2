import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as mpl_cm
import palettable.colorbrewer as cb
from .scaled_ticks import ScaledLocator, ScaledFormatter, LsFormatter
from ..core import variables
import numpy as np

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
    
