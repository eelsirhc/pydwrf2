import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xarray
from ..core import variables
import numpy as np

def lsticks(cls):
    plt.xlabel("L_S")
    dls = (cls[-1]-cls[0])/360.
    if dls > 10.:
        delta = 360
        tr = lambda x: x/360.
    elif dls >2:
        delta = 90
        tr = lambda x: x%360
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
            data = input[variable]
            if len(data.shape) != 1:
                raise Exception("Data needs to be 1 dimensional")
            plt.figure(figsize=(12,3))
            cls = variables.continuous_ls(input["L_S"])
            C = plt.plot(cls,data)
            lsticks(cls)
            plt.tight_layout()
            plt.savefig(output_filename)
    except Exception as e:
        raise
    finally:
        pass
        
        
def quick_plot_2d(filename, output_filename, variable):
    try:
        with xarray.open_dataset(filename) as input:
            data = input[variable]
            if len(data.shape) != 2:
                raise Exception("Data needs to be 2 dimensional")
            plt.figure(figsize=(12,3))
            cls = variables.continuous_ls(input["L_S"])
            C = plt.pcolormesh(cls,variables.latitude(input), data.T)
            plt.ylabel("Latitude")
            plt.yticks([-90,-45,0,45,90])
            lsticks(cls)
            CB = plt.colorbar()
            CB.set_label(variable)
            plt.tight_layout()
            plt.savefig(output_filename)
    except Exception as e:
        raise
    finally:
        pass
        

def quick_plot(filename, output_filename, variable):
    try:
        func = {1:quick_plot_1d, 2:quick_plot_2d}
        
        with xarray.open_dataset(filename) as input:
            data = input[variable]
            s = len(data.shape)
        func[s](filename, output_filename, variable)
    except Exception as e:
        raise


