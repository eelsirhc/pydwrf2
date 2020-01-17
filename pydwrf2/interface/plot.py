"""CLI for plotting WRF data"""
import argh
import numpy as np

#from .common import


def csv(st):
    print(st)
    return st.split(",")

@argh.arg("variable",type=csv)
def quick_plot(filename, output_filename, variable):
    try:
        import xarray
        from ..plots import quick_plot_1d, quick_plot_2d
        func = {1:quick_plot_1d, 2:quick_plot_2d}
        print(variable)
        print(variable)
        with xarray.open_dataset(filename) as input:
            data = input[variable]
            print(data.sizes)
            s = len(data.sizes)
        func[s](filename, output_filename, variable)
    except Exception as e:
        raise


def qp(filename, output_filename, var):
    print("spo")


def t15(t15_filenames, output_filename, labels="", observation=True):
    from ..wrf import t15 as t15m
    t15m.plot_t15(t15_filenames, output_filename, labels=labels,observation=observation)


def lander(lander_filenames, output_filename, labels="", observation=True):
    from ..wrf import vl
    vl.plot_lander(lander_filenames, output_filename, labels=labels, observation=observation)


def icemass(ice_filenames, output_filename, labels="", observation=True, wrap=False):
    from ..wrf import icemass
    icemass.plot_icemass(ice_filenames, output_filename, labels=labels, observation=observation, wrap=wrap)


def eq_taudust(dust_filenames, output_filename, labels="", observation=True):
    from ..wrf import dust
    dust.plot_dust_scaled(dust_filenames, output_filename, labels=labels, observation=observation)


def print_args(arguments, input_filenames, output_filename, observation=True):
    print(arguments, input_filenames, output_filename, observation)


cli = dict(name="plot", commands=[quick_plot,
                                  qp,
                                  t15,
                                  lander,
                                  icemass,
                                  eq_taudust,
                                  print_args])
