import xarray
import pandas as pd
import json
import os
import numpy as np
from tqdm import tqdm
from ..wrf import dates
import logging


def write_if_changed(dataframe, filename, index_label="Times"):
    """Write the pandas dataframe only if it's different to the file."""

    old_df = None
    if os.path.exists(filename):
        old_df = pd.read_csv(filename, index_col=0)
        old_mtime = os.path.getmtime(filename)

    update_file = True
    if old_df is not None and dataframe.index.equals(old_df.index):
        update_file = False

    if update_file:
        print("Updating {}".format(filename))
        directory = os.path.dirname(filename)
        if directory is not "" and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        dataframe.to_csv(filename, index_label=index_label)


def sumsquare(d, axis=None):
    return np.mean(np.multiply(d, d), axis)


def suffix(xa, suffix):
    names = dict(zip(xa.variables,
                                ("{}{}".format(k,suffix) for k in xa.variables)))
    if "hour" in names:
        del names["hour"]
    return xa.rename( names )


def aggregate(variable, index_filename, output_filename, aggregation):
    """Dumb average of data"""
    index = pd.read_csv(index_filename, index_col=0)
    local_time_dimension = index["Hour"].unique()
    data = []
    ntime = len(local_time_dimension)

    vv = variable.split(",") + ["hour"]
    
    for filename in tqdm(index["Filename"].unique()):
        local_df = index[index["Filename"]==filename]
        nc = xarray.open_dataset(filename)
        nc["hour"] = xarray.DataArray(dates.get_hours(nc["Times"]), dims="Time")
        if "PRES" in vv:
            nc["PRES"] = nc["P"] + nc["PB"]
        if "TEMP" in vv:
            nc["TEMP"] = (nc["T"] + nc.T0)*((nc["P"]+nc["PB"])/nc.P0)**(nc.R_D/nc.CP)

        mydata = nc[vv].isel(Time=local_df["File_Counter"]).reset_coords()
        g = mydata.groupby("hour")
        data.append(dict(sum=g.sum(["Time"]),
                         count=g.count(["Time"]),
                         max=g.max(["Time"]),
                         min=g.min(["Time"]),
                         sqs=g.reduce(sumsquare, dim=["Time"])))

  
    total_count = xarray.concat((d["count"] for d in data),dim="ensemble").groupby("hour").sum("ensemble")
    total = xarray.Dataset()
   
    if "mean" in aggregation:
        total_mean = xarray.concat((d["sum"]/total_count for d in data),dim="ensemble").groupby("hour").sum("ensemble")
        total = total.merge(suffix(total_mean,"_mean"))

    if "std" in aggregation:
        if "mean" not in aggregation:
            total_mean = xarray.concat((d["sum"]/total_count for d in data),dim="ensemble").groupby("hour").sum("ensemble")
        total_std = xarray.concat((d["sqs"]/total_count for d in data),dim="ensemble").groupby("hour").sum("ensemble")
        total_std = (total_std - total_mean**2)*0.5
        
        total = total.merge(suffix(total_std,"_std"))

    if "max" in aggregation:
        #max
        group_max = (xarray.concat((d["max"] for d in data),dim="ensemble").
                     groupby("hour").
                     max("ensemble"))
        
        total = total.merge(suffix(group_max,"_max"))

    if "min" in aggregation:
        #min
        group_min = (xarray.concat((d["min"] for d in data),dim="ensemble").
                     groupby("hour").
                     max("ensemble"))

        total = total.merge(suffix(group_min,"_min"))

    total.to_netcdf(output_filename)


def index_ls(low, high,
    database_filename="output/database/database_index.csv",
    database_ls_prefix="output/database/database-ls",
    partial_sol=True,
    format_string="05.1f"):
    """Create an L_S specfic index.

    This file acts as a gateway to remaking a database file.
    """
    df = pd.read_csv(database_filename, index_col=0)
    # reset the extreme ls values

    df.at[df["L_S"] == 360.0, "L_S"] = 0.0
    if low > high:
        select = ((df["L_S"] >= low) & (df["L_S"] < 360.0) |
                 (df["L_S"] >= 0.0) & (df["L_S"] < high))
    else:
        select = (df["L_S"] >= low) & (df["L_S"] < high)

    if not partial_sol:
        for sol in df["Sol"][select].unique():
            select = select | (df["Sol"] == sol)

    filename = database_ls_prefix + "-{}-{}.csv".format(format(low,format_string),
                                                        format(high,format_string))
    write_if_changed(df[select], filename)



def _index_one_file(filename, source_filename=None):
    columns = [
        "File_Counter",
        "Filename",
        "L_S",
        "Times",
        "Year",
        "Sol",
        "Hour",
        "Minute",
        "Second",
    ]
    result = []
    if filename is not None:
        nc = xarray.open_dataset(filename)
        ls = nc["L_S"]
        times = nc["Times"]
        date = dates.parse_dates(times)
        file_counter = 0
        for l, t, d in zip(ls.values, times.values, date):
            myr = [file_counter, filename, l, t.decode("utf-8")]
            if source_filename is not None:
                myr[1] = source_filename
            myr.extend(d)
            result.append(myr)
            file_counter += 1
    df = pd.DataFrame(result, columns=columns).set_index("Times")
    return df


def index_one_file(filename, output_filename):
    table = _index_one_file(filename)
    write_if_changed(table, output_filename)


def index(index_filename="output/index",
    database_filename="output/database/database_index.csv",
    intermediate="output/intermediate"):
    """Create a new index file for the database.

    Each line includes an index number into each file from the entire wrfout collection
    and the L_S and local time of that index."""

    # 1. Load the JSON file that contains the wrfout files that we are indexing
    import json
    import xarray
    import pandas as pd
    from tqdm import tqdm


    filepaths = json.load(open(index_filename, "r"))
    old_df = _index_one_file(None)
    old_mtime = 0

    if os.path.exists(database_filename):
        old_df = pd.read_csv(database_filename, index_col=0)
        old_mtime = os.path.getmtime(database_filename)
    result = []
    # counter=0
    # 2. Loop through the wrfout files
    for filename in tqdm(filepaths.get("wrfout", [])):
        ls_filename = os.path.join(intermediate,os.path.basename(filename)+".ls")
        if old_mtime > os.path.getmtime(ls_filename) and ls_filename in old_df["Filename"]:
            print("Found unmodified data")
            continue
        # 2.a Load the file
        myr = _index_one_file(ls_filename, source_filename=filename)
        result.append(myr)
    df = pd.concat(result)
        
    # 3. Check for the old database file
    # 4. Compare the two database files
    update_file = True

    if len(old_df):
        new_df = pd.concat([old_df, df])
        new_df = new_df.loc[~new_df.index.duplicated(keep="first")]
    else:
        new_df = df.copy()

    if old_df is not None and new_df.index.equals(old_df.index):
        update_file = False

    # 5. If the data is modified, write a new file

    if update_file:
        print("Updating database index file")
        directory = os.path.dirname(database_filename)
        if directory is not "" and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        new_df.to_csv(database_filename, index_label="Times")


def register(com):
    com.add_command(database)
