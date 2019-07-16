import matplotlib

matplotlib.use("Agg")
import xarray
import logging
import matplotlib.pyplot as plt
import os
import numpy as np
from . import scaled_ticks as st


def continuous_ls(ls):
    """Tries to convert Ls values to be continuous.
    Does this by looking for negative changes in Ls values and assumes that's the next year of data"""
    loop = -1
    old = 360.0
    for i, v in enumerate(ls):
        if v < old + 1e-5:
            loop += 1
        ls[i] += loop * 360.0
        old = v
    return ls


def split_ls(x, y):
    """Find the locations of negative changes in Ls and returns a tuple of Ls and 'data' split into the Ls groups"""
    start = 0
    xx = []
    yy = []
    for i in range(x.size - 1):
        if x[i + 1] < x[i]:
            xx.append(x[start : i + 1])
            yy.append(y[start : i + 1])
            start = i + 1

    xx.append(x[start:])
    yy.append(y[start:])
    return xx, yy


def plot_core(ax, x, y, scale=1.0, *args, **kwargs):
    """Core plot function. 
        Args:
            ax (Axis) : The axis to plot on
            x: x data
            y: y data
            scale: (optional) scale data by the scale factor

        Returns:
            plot object
    """
    sval=1.0
    # sval = convert_scale(scale)
    P = ax.plot(x, y * sval, *args, **kwargs)
    return P


def ls_plot(x, y, loop=False, ylabel=None, cycle_colors=False, *args, **kwargs):
    """
        Plot against Ls and mark the x-axis appropriately
        Args:
            x: x data
            y: y data
            loop: (optional) True loops the data onto the same Ls range, False plots a continuous Ls
            ylab: (optional) y label
            cycle_colors: (optional) if True inhibits the changing of colors with each line from the same dataset
        Returns:
            plot object(s)
    """
    ax = plt.gca()
    if not loop:
        xax = continuous_ls(x)
        P = plot_core(ax, xax, y, *args, **kwargs)
    else:
        xax = x
        xs, ys = split_ls(x, y)
        P = []
        color = None
        incoming_color = "color" in kwargs
        for i, xx in enumerate(zip(xs, ys)):
            if i > 0 and not incoming_color and not cycle_colors:
                kwargs["color"] = base_line.get_color()
                kwargs["label"] = None
            base_line, = plot_core(ax, xx[0], xx[1], *args, **kwargs)
            P.append(base_line)

    l, h = np.floor(xax.min() / 90) * 90, np.ceil((xax.max() + 1) / 90) * 90
    t = np.arange(l, h + 45, 90)
    ax.set_xticks(t)
    ax.xaxis.set_major_formatter(st.LsFormatter())
    ax.set_xlabel("Ls")

    if ylabel is not None:
        ax.set_ylabel(ylabel)
    return P


def plot_line(filename, output_filename, variable):
    with xarray.open_dataset(filename) as input:
        ls = input["ls"] if "ls" in input else input["L_S"]
        data = input[variable]

        plt.figure(figsize=(8, 8))
        ls_plot(ls, data, loop=True, label=variable)

        plt.gca().set_xlabel("Ls")
        plt.gca().set_ylabel(variable)
        plt.legend(loc="upper left")
        plt.savefig(output_filename)
    return None
