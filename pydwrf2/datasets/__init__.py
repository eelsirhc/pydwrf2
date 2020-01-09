"""Interacts with datasets held remotely."""

from os.path import dirname, join, exists
import pandas as pd
from .utils import fetch_dataset, RemoteFileMetadata, get_data_home

DEFAULT_REMOTE = "remote_data.csv"
def load_data(name, remote=None):
    """Load a named dataset from a remote location.

    Assuming that dataset is named in the remote location
    Args:
        name : Name of the dataset
    Options :
        remote : remote data table.
    """

    module_path = dirname(__file__)
    if remote is None:
        remote_data = join(module_path, DEFAULT_REMOTE)
    else:
        remote_data = remote

    table = pd.read_csv(remote_data)
    if any(table["name"] == name):
        data = [v for k, v in table[table["name"] == name].iterrows()]
        return fetch_dataset(data)
    else:
        raise NameError("{} not found".format(name))


def list_data(remote, full=False):
    """List the data available from the remote.

    If no remote is given, use the default.
    Args:
        remote: remote filename or None
    Options:
        full : flag, True to print out all data in the table.
    """
    module_path = dirname(__file__)
    if remote is None:
        remote_data = join(module_path, DEFAULT_REMOTE)
    else:
        remote_data = remote

    table = pd.read_csv(remote_data)
    home = get_data_home(data_home=None)

    for _, row in table.iterrows():
        if not full:
            print(row["name"], row["filename"])
        else:
            print(row["name"])
            for key in ["filename", "url", "checksum"]:
                print("\t{}".format(row[key]))
            print("\t!downloaded" if exists(join(home,row["filename"]))
                  else "\tnot downloaded")
