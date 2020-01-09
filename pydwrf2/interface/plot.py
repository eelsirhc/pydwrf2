"""CLI for plotting WRF data"""
import click

import xarray
import pandas as pd
import numpy as np

from ..datasets import load_data

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
def cli():
    """Plot data from WRF output files and processed data."""
    pass


@cli.command()
@click.argument("filename")
@click.argument("output_filename")
@click.argument("variable")#, type=CSVType())
def quick_plot(filename, output_filename, variable):
    try:
        from ..plots import quick_plot_1d, quick_plot_2d
        func = {1:quick_plot_1d, 2:quick_plot_2d}
        print(variable)
        with xarray.open_dataset(filename) as input:
            data = input[variable[0]]
            s = len(data.shape)
        func[s](filename, output_filename, variable)
    except Exception as e:
        raise


@cli.command()
@click.argument("filename",type=str)
@click.argument("output_filename",type=str)
@click.argument("var",type=str)#, type=CSVType())
def qp(filename, output_filename, var):
    print("spo")



@cli.command()
@click.argument("t15_filenames")
@click.argument("output_filename")
@click.option("--labels", default="")
@click.option("--observation/--no-observation", is_flag=True, default=True)
def t15(t15_filenames, output_filename, labels="", observation=True):
    from ..wrf import t15 as t15m
    t15m.plot_t15(t15_filenames, output_filename, labels=labels,observation=observation)


@cli.command()
@click.argument("lander_filenames", type=CSVType())
@click.argument("output_filename")
@click.option("--labels", default="", type=CSVType())
@click.option("--observation/--no-observation", is_flag=True, default=True)
def lander(lander_filenames, output_filename, labels="", observation=True):
    from ..wrf import vl
    vl.plot_lander(lander_filenames, output_filename, labels=labels, observation=observation)


@cli.command()
@click.argument("ice_filenames")
@click.argument("output_filename")
@click.option("--labels", default="")
@click.option("--observation/--no-observation", is_flag=True, default=True)
@click.option("--wrap/--no-wrap", is_flag=True, default=False)
def icemass(ice_filenames, output_filename, labels="", observation=True, wrap=False):
    from ..wrf import icemass
    icemass.plot_icemass(ice_filenames, output_filename, labels=labels, observation=observation, wrap=wrap)


@cli.command()
@click.argument("dust_filenames")
@click.argument("output_filename")
@click.option("--labels", default="")
@click.option("--observation/--no-observation", is_flag=True, default=True)
def eq_taudust(dust_filenames, output_filename, labels="", observation=True):
    from ..wrf import dust
    dust.plot_dust_scaled(dust_filenames, output_filename, labels=labels, observation=observation)


@cli.command()
@click.argument("arguments")
@click.argument("input_filenames")
@click.argument("output_filename")
@click.option("--observation/--no-observation", is_flag=True, default=True)
def print(arguments, input_filenames, output_filename, observation=True):
    print(arguments, input_filenames, output_filename, observation)

