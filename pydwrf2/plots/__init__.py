import matplotlib
matplotlib.use("Agg")
import xarray
from ..core import variables
from . import core
import numpy as np
import matplotlib.pyplot as plt


def lsticks(cls):
    plt.xlabel("L_S")
    dls = (cls[-1]-cls[0])/360.
    if dls > 10.:
        delta = 360
        tr = lambda x: x/360.
    elif dls >2:
        delta = 90
        tr = lambda x: (x%360).astype(int)
    else:
        delta = 45
        tr = lambda x: x%360
    xt = np.arange((cls[0]//delta)*delta,
                       (cls[-1]//delta+1)*delta,
                       delta)
        
    plt.xticks(xt,tr(xt))

def quick_plot_1d(filename, output_filename, variable):
    try:
        with xarray.open_dataset(filename) as input:
            data = input[variable[0]]
            if len(data.shape) != 1:
                raise Exception("Data needs to be 1 dimensional")
            plt.figure(figsize=(12,3))
            cls = variables.continuous_ls(input["L_S"])
            for v in variable:
                data = input[v]
                C = plt.plot(cls,data,label=v)
            plt.legend()
            lsticks(cls)
            plt.tight_layout()
            plt.savefig(output_filename)
    except Exception as e:
        raise
    finally:
        pass
        

def quick_plot_2d(filename, output_filename, variable_list):
    try:
        pc = core.Configuration()
        with xarray.open_dataset(filename) as input:
            from matplotlib.backends.backend_pdf import PdfPages
            with PdfPages(output_filename) as pdf:
                for variable in variable_list:
                    options = pc.options(variable)
                    data = input[variable]
                    if len(data.shape) != 2:
                        raise Exception("Data needs to be 2 dimensional")
                    plt.figure(figsize=(12,3))
                    cls = variables.continuous_ls(input["L_S"])

                    if "cmap" not in options:
                        options["cmap"] = "viridis"

                    from matplotlib.ticker import MaxNLocator
                    from matplotlib.colors import BoundaryNorm

                    if "levels" not in options:
                        options["levels"] = MaxNLocator(nbins=15).tick_values(data.min().values, data.max().values)
                    cmap = plt.get_cmap(options["cmap"])
                    norm = BoundaryNorm(options["levels"], ncolors=cmap.N, clip=True)
                        
                    C = plt.pcolormesh(cls,variables.latitude(input), data.T, norm=norm, cmap=cmap)
                    plt.ylabel("Latitude")
                    plt.yticks([-90,-45,0,45,90])
                    lsticks(cls)
                    CB = plt.colorbar()
                    CB.set_label(variable)
                    plt.tight_layout()
                    pdf.savefig()
                    plt.close()
    except Exception as e:
        raise
    finally:
        pass
        
