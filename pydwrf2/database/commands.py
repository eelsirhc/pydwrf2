import xarray
import pandas as pd
import json
import click
import os
from ..wrf import dates

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


@click.group()
def database():
    pass


@database.command()
@click.argument("low", type=float)
@click.argument("high", type=float)
@click.option(
    "--database_filename", type=str, default="output/database/database_index.csv"
)
@click.option("--database_ls_prefix", type=str, default="output/database/database_ls")
@click.option("--partial_sol", is_flag=True, default=False)
def index_ls(low, high, database_filename, database_ls_prefix, partial_sol):
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

    filename = database_ls_prefix + "_{}_{}.csv".format(low, high)
    write_if_changed(df[select], filename)
    


@database.command()
@click.option("--index_filename", type=str, default="output/index")
@click.option(
    "--database_filename", type=str, default="output/database/database_index.csv"
)
def index(index_filename, database_filename):
    """Create a new index file for the database.

    Each line includes an index number into each file from the entire wrfout collection
    and the L_S and local time of that index."""

    # 1. Load the JSON file that contains the wrfout files that we are indexing
    import json
    import xarray
    import pandas as pd
    from tqdm import tqdm


    filepaths = json.load(open(index_filename, "r"))

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
    old_df = pd.DataFrame([], columns=columns).set_index("Times")
    old_mtime = 0

    if os.path.exists(database_filename):
        old_df = pd.read_csv(database_filename, index_col=0)
        old_mtime = os.path.getmtime(database_filename)
    result = []
    # counter=0
    # 2. Loop through the wrfout files
    for filename in tqdm(filepaths.get("wrfout", [])):
        if old_mtime > os.path.getmtime(filename) and filename in old_df["Filename"]:
            print("Found unmodified data")
            continue

        # 2.a Load the file
        nc = xarray.open_dataset(filename)
        # 2.b read in L_S, times
        ls = nc["L_S"]
        times = nc["Times"]
        date = dates.parse_dates(times)
        # 2.c add in each entry into the table
        file_counter = 0
        for l, t, d in zip(ls.values, times.values, date):
            myr = [file_counter, filename, l, t.decode("utf-8")]
            myr.extend(d)
            result.append(myr)
            #            counter+=1
            file_counter += 1
    df = pd.DataFrame(result, columns=columns).set_index("Times")
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
