import xarray
import numpy as np
from ..datasets import load_data
import pandas as pd

# Pressure grid for the interpolation
pw = np.exp(((1 + np.arange(62)) / 10.0) - 4.6)

# Weighting function for the brightness temperature calculation
wtfcn = np.array(
    [
        0.03500,
        0.03500,
        0.03600,
        0.03600,
        0.03700,
        0.03700,
        0.03800,
        0.03900,
        0.04100,
        0.04300,
        0.04600,
        0.04900,
        0.05200,
        0.05600,
        0.06000,
        0.06500,
        0.07000,
        0.07600,
        0.08200,
        0.09000,
        0.09700,
        0.10500,
        0.11500,
        0.12500,
        0.13600,
        0.14700,
        0.15900,
        0.17200,
        0.18600,
        0.20100,
        0.21700,
        0.23400,
        0.25200,
        0.27000,
        0.28800,
        0.30800,
        0.32600,
        0.34300,
        0.36000,
        0.37200,
        0.38200,
        0.38800,
        0.39100,
        0.38800,
        0.37900,
        0.36400,
        0.34200,
        0.31000,
        0.27800,
        0.24600,
        0.21300,
        0.17800,
        0.14300,
        0.10900,
        0.08100,
        0.06100,
        0.04500,
        0.03200,
        0.02200,
        0.01500,
        0.01000,
        0.00700,
    ]
)

# wtfcn = np.reshape(wtfcn,(62, wtfcn.size/62))
wtfcn = np.reshape(wtfcn, (62, int(wtfcn.size / 62)))


def t15data():
    """T15 data based on Claire Newman's interpolation of Basu 2002 paper."""
    ls = np.arange(73) * 5.0
    t = np.array(
        [
            175.6,
            173.8,
            172.6,
            171.4,
            170.2,
            169.1,
            168.1,
            167.2,
            166.4,
            165.8,
            165.8,
            166.0,
            166.2,
            166.5,
            166.8,
            167.1,
            167.4,
            167.7,
            168.0,
            168.65,
            169.3,
            169.95,
            170.6,
            171.3,
            172.0,
            172.7,
            173.4,
            174.15,
            174.9,
            175.7,
            176.5,
            177.25,
            178.0,
            178.7,
            179.4,
            180.0,
            180.8,
            181.6,
            182.4,
            183.2,
            184.0,
            184.8,
            185.6,
            186.4,
            187.2,
            188.05,
            188.9,
            189.8,
            190.7,
            191.35,
            191.95,
            191.75,
            191.15,
            190.55,
            190.0,
            189.3,
            188.6,
            187.9,
            187.2,
            186.5,
            185.8,
            185.15,
            184.55,
            184.0,
            183.4,
            182.8,
            182.15,
            181.4,
            180.6,
            179.4,
            178.6,
            177.6,
            175.8,
        ]
    )
    return ls, t


try:
    # Doesn't seem faster right now.
    raise
    # Try importing Just-In-Time (jit) compiler from numba
    from numba import jit

    @jit
    def interp(p, t, pw):
        """Using jit compiler to run faster interpolation"""
        j = 0
        tw = np.zeros(pw.size)
        for i in np.arange(pw.size):
            if pw[i] < p[0]:
                tw[i] = t[0]
            elif pw[i] >= p[-1]:
                tw[i] = t[-1]
            else:
                while p[j + 1] < pw[i]:
                    j = j + 1
                k2 = j + 1
                k1 = j
                tw[i] = ((p[k2] - pw[i]) * t[k1] + (pw[i] - p[k1]) * t[k2]) / (
                    p[k2] - p[k1]
                )
        return tw

except Exception:
    from scipy.interpolate import interp1d

    def interp(p, t, pw):
        out = interp1d(
            p[::-1],
            t[::-1],
            kind="linear",
            copy=False,
            bounds_error=False,
            fill_value=(t[0], t[-1]),
        )(pw)
        return out


def t15_core_fast(press, temp, area):
    """Calculate area weighted mean brightness temperature at 15 microns
        First interpolate temperature profile to pressure values, then use
        weighting function to calculate brightness temperature.
    """
    # area weighted mean temperature
    #    mean_temp = np.average(
    #        np.average((temp * area[None, :, :]), axis=1), axis=0
    #    ) / np.average(area)
    y = 0
    tb15av = 0.0
    arav = 0.0
    f = None
    tw = np.zeros(pw.shape)
    arav = 1
    temp = temp[::-1]
    press = 0.01 * press[::-1]
    tw = np.zeros((temp.shape[1], temp.shape[2], pw.shape[0]))

    for i in np.arange(temp.shape[1]):
        for j in np.arange(temp.shape[2]):
            t, p = temp[::-1, i, j], press[::-1, i, j] * 0.01  # reversed
            tw[i, j] = interp(press[:, i, j], temp[:, i, j], pw)

    rad = -0.0181075 - 39.4312 / (
        tw - 2353.76 - 62644.0 / (tw + 64.445 + 84263.9 / (tw - 185.333))
    )

    radsum = (rad * wtfcn[:, y]).sum(axis=-1)
    sumwt = sum(wtfcn[:, y])
    xx = radsum / sumwt

    tb15 = 881.042 - 2.40183 / (
        xx
        + 0.00364298
        - 0.61044e-7 / (xx + 0.162965e-3 - 0.113959e-8 / (xx + 0.228812e-4))
    )

    tb15av = (tb15 * area).sum() / area.sum()
    return tb15av
    # return 0


def t15_core_slow(press, temp, area):
    """Calculate area weighted mean brightness temperature at 15 microns
        First interpolate temperature profile to pressure values, then use
        weighting function to calculate brightness temperature.
    """
    # area weighted mean temperature
    #    mean_temp = np.average(
    #        np.average((temp * area[None, :, :]), axis=1), axis=0
    #    ) / np.average(area)
    y = 0
    tb15av = 0.0
    arav = 0.0
    f = None
    tw = np.zeros(pw.shape)
    arav = 1
    for i in np.arange(temp.shape[1]):
        for j in np.arange(temp.shape[2]):
            t, p = temp[::-1, i, j], press[::-1, i, j] * 0.01  # reversed
            tw = interp(p, t, pw)
            rad = -0.0181075 - 39.4312 / (
                tw - 2353.76 - 62644.0 / (tw + 64.445 + 84263.9 / (tw - 185.333))
            )

            radsum = sum(rad * wtfcn[:, y])
            sumwt = sum(wtfcn[:, y])
            xx = radsum / sumwt

            tb15 = 881.042 - 2.40183 / (
                xx
                + 0.00364298
                - 0.61044e-7 / (xx + 0.162965e-3 - 0.113959e-8 / (xx + 0.228812e-4))
            )
            tb15av = tb15av + tb15 * area[i, j]
            arav = arav + area[i, j]
    return tb15av / arav


def process_file(filename, rows=None):
    """Process a file.

    Extract variables from the netCDF file, calculate
    the temperature from potential temperature.
    Then pass T,P into the t15_core function to calculate T15 values.
    """
    nc = xarray.open_dataset(filename)
    xlat = nc["XLAT"][0, :, :]
    xlong = nc["XLONG"][0, :, :]
    xlong_u = nc["XLONG_U"][0, :, :]
    xlat_v = nc["XLAT_V"][0, :, :]
    dlat = np.diff(xlat_v, axis=0)
    dlong = np.diff(xlong_u, axis=1)

    radius = nc.RADIUS
    area = (
        radius
        * radius
        * (1.0 / xlat.shape[-1])
        * 2
        * np.pi
        * (np.sin(np.deg2rad(xlat_v[1:])) - np.sin(np.deg2rad(xlat_v[:-1])))
    )
    g = nc.G
    omega = nc.EOMEG
    cp = nc.CP
    rd = nc.R_D
    kappa = rd / cp
    t0 = nc.T0
    p0 = nc.P0

    lat = xlat[:, 0]

    l_s, P, PB, T = [nc.variables[x] for x in ["L_S", "P", "PB", "T"]]
    latsel = np.where((xlat[:, 0] >= -40.0) & (xlat[:, 0] < 40))[0]
    latsel = slice(latsel[0], latsel[-1], 1)

    tvals = []
    rows = rows or slice(None)
    rows = np.arange(T.shape[0])[rows].astype(int)
    from tqdm import tqdm

    for i in rows:
        press = P[i, :, latsel] + PB[i, :, latsel]
        theta = T[i, :, latsel] + t0
        temp = (press / p0) ** kappa * theta
        t15_values = t15_core_fast(press, temp, area[latsel])
        tvals.append(t15_values)
    t15=xarray.DataArray(np.array(tvals),dims=["Time"],
                         attrs = dict(description="15 micron temperature calculated based on Basu(2002)"))
    data = dict(ls=l_s[rows], 
                t15=t15)

    data["times"] = nc["Times"]
    
    return data


def plot_t15(t15_filenames, output_filename, labels="", observation=True):
    from ..plots import core
    plt = core.plt
    
    fig = plt.figure(figsize=(8,6))
    ax = fig.gca()
    filename_list = [x for x in t15_filenames.split(",") if len(x)]
    labels_list = [x for x in labels.split(",") if len(x)]

    if len(labels_list) < len(filename_list):
        labels_list.extend(filename_list[len(labels_list):])


    #TODO : move me.

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
