import matplotlib.pyplot as plt

import xarray
from ..plots import quick_plot_1d, quick_plot_2d
import click
from . import core
from ..datasets import load_data
import pandas as pd
import numpy as np
class CSVType(click.ParamType):
        name = 'csv'

        def convert(self, value, param, ctx):
            if isinstance(value, bytes):
                try:
                    enc = getattr(sys.stdin, 'encoding', None)
                    if enc is not None:
                        value = value.decode(enc)
                except UnicodeError:
                    try:
                        value = value.decode(sys.getfilesystemencoding())
                    except UnicodeError:
                        value = value.decode('utf-8', 'replace')
                return value.split(',')
            return value.split(',')

        def __repr__(self):
            return 'CSV'

@click.group()
def plots():
    pass

@plots.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("output_filename")
@click.argument("variable", type=CSVType())
def quick_plot(filename, output_filename, variable):
    try:
        func = {1:quick_plot_1d, 2:quick_plot_2d}
        print(variable)
        with xarray.open_dataset(filename) as input:
            data = input[variable[0]]
            s = len(data.shape)
        func[s](filename, output_filename, variable)
    except Exception as e:
        raise

#@plots.command()
#@click.argument("filename")
#@click.argument("output_filename")
#@click.argument("variable"
#def multi_file_plot(filenames, labels, output_filename, variable):
#    print(filenames)
#    try:
#        input_0 = xarray.open_dataset(filenames[0])
#        data_shape = input_0[variable[0]].shape
#        input_0.close
#        if len(data_shape) != 1:
#            raise Exception("Data needs to be 1 dimensional")
#            
#        plt.figure(figsize=(12,3))
#        for v in variable:
#            if len(labels) != len(filenames):
#                labels=filenames
#            for name, label in zip(filenames, labels):
#                with xarray.open_dataset(name) as input:
#                    cls = variables.continuous_ls(input["L_S"])
#                    data = input[v]
#                    C = plt.plot(cls,data,label=label)
#            plt.legend()
#            lsticks(cls)
#            plt.tight_layout()
#            plt.title(v)
#            plt.savefig(output_filename)
#    except Exception as e:
#        raise
#    finally:
#        pass


@plots.command()
@click.argument("t15_filenames")
@click.argument("output_filename")
@click.option("--labels", default="")
@click.option("--observation/--no-observation", is_flag=True, default=True)
def plot_t15(t15_filenames, output_filename, labels="", observation=True):
    fig = plt.figure(figsize=(8,6))
    ax = fig.gca()
    filename_list = [x for x in t15_filenames.split(",") if len(x)]
    labels_list = [x for x in labels.split(",") if len(x)]

    if len(labels_list) < len(filename_list):
        labels_list.extend(filename_list[len(labels_list):])


    limits = np.array([np.nan,np.nan,np.nan,np.nan])
            
    for label,filename in zip(labels_list, filename_list):
        with xarray.open_dataset(filename) as nc:
            h, mylimits = core.plotline(nc["L_S"], nc["t15"],True, label=label)
            limits = core.replace_limits(limits, mylimits)
            
    if observation:
        # download the observation
        package = load_data("t15")
        for k,v in package.items():
            if v["status"] and k.count("t15"):
                # read the observation
                df = pd.read_csv(v["location"], comment="#")
                # plot the observation
                core.plotline(df["ls"],df["t15"],True, label="observation")
                
        plt.legend()
    plt.savefig(output_filename)


@plots.command()
@click.argument("lander_filenames", type=CSVType())
@click.argument("output_filename")
@click.option("--labels", default="", type=CSVType())
@click.option("--observation/--no-observation", is_flag=True, default=True)
def plot_lander(lander_filenames, output_filename, labels="", observation=True):
        from ..wrf import vl
        vl.plot_lander(lander_filenames, output_filename, labels=labels, observation=observation)
    
@plots.command()
@click.argument("ice_filenames")
@click.argument("output_filename")
@click.option("--labels", default="")
@click.option("--observation/--no-observation", is_flag=True, default=True)
def plot_icemass(ice_filenames, output_filename, labels="", observation=True):
    from ..wrf import icemass
    icemass.plot_icemass(ice_filenames, output_filename, labels=labels, observation=observation)


@plots.command()
@click.argument("dust_filenames")
@click.argument("output_filename")
@click.option("--labels", default="")
@click.option("--observation/--no-observation", is_flag=True, default=True)
def plot_taudust(dust_filenames, output_filename, labels="", observation=True):
    from ..wrf import dust
    dust.plot_dust_scaled(dust_filenames, output_filename, labels=labels, observation=observation)


@plots.command()
@click.argument("arguments")
@click.argument("input_filenames")
@click.argument("output_filename")
@click.option("--observation/--no-observation", is_flag=True, default=True)
def plot(arguments, input_filenames, output_filename, observation=True):
    print(arguments, input_filenames, output_filename, observation)

    
def register(com):
    for entry in [quick_plot,
                  plot_t15,
                  plot_icemass,
                  plot_taudust,
                  plot_lander,
                  plot]:
        com.add_command(entry)
