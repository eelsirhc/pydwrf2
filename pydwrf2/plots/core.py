import matplotlib.cm as mpl_cm
import palettable.colorbrewer as cb
from scaled_ticks import ScaledLocator, ScaledFormatter, LsFormatter

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

