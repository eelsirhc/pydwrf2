import xarray
import click


@click.group()
def database():
    pass

@database.command()
@click.option("--index_filename", type=str, default="output/index")
@click.option("--database_index", type=str, default="output/database/database_index.csv")
def database_index(index_filename, database_index):
    """Create a new index file for the database.

    Each line includes an index number into each file from the entire wrfout collection
    and the L_S and local time of that index."""

    #1. Load the JSON file that contains the wrfout files that we are indexing
    import json
    import xarray
    import pandas as pd
    from tqdm import tqdm
    import os
    from ..wrf import dates
    filepaths = json.load(open(index_filename,"r"))

    columns=["File_Counter","Filename","L_S","Times","Year","Sol","Hour","Minute","Second"]
    old_df = pd.DataFrame([], columns=columns)
    old_mtime = 0

    if os.path.exists(database_index):
        old_df = pd.read_csv(database_index)
        old_mtime = os.path.getmtime(database_index)
    
    result = []
    #counter=0
    #2. Loop through the wrfout files
    for filename in tqdm(filepaths.get("wrfout",[])):
        if (old_mtime > os.path.getmtime(filename) and
            filename in old_df["Filename"]):
            print("Found unmodified data")
            continue
                  
           
        
        #2.a Load the file
        nc = xarray.open_dataset(filename)
        #2.b read in L_S, times
        ls = nc["L_S"]
        times = nc["Times"]
        date = dates.parse_dates(times)
        #2.c add in each entry into the table
        file_counter=0
        for l,t,d in zip(ls.values, times.values,date):
            myr = [file_counter,filename,l,t]
            myr.extend(d)
            result.append(myr)
#            counter+=1
            file_counter+=1
    df = pd.DataFrame(result,columns=columns)
    #3. Check for the old database file
    #4. Compare the two database files
    update_file = True

    new_df = df.merge(old_df)
    new_df.index = np.arange(len(new_df))
    if old_df is not None and new_df.equals(old_df):
        update_file = False

    #5. If the data is modified, write a new file
    print(new_df)
    if update_file:
        os.makedirs(os.path.dirname(database_index),exist_ok=True)
        new_df.to_csv(database_index)


def register(com):
    for entry in [database_index]:
        com.add_command(entry)
