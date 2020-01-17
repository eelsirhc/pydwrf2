"""Interacts with datasets held remotely."""

from os.path import dirname, join, exists
import yaml
from .utils import fetch_dataset, RemoteFileMetadata, get_data_home

DEFAULT_REMOTE = "remote_data.yaml"
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

    table = yaml.safe_load(open(remote_data,'r'))
    if name in table:
        return fetch_dataset(table[name])
    else:
        raise NameError("{} not found".format(name))


def list_data(remote=None, full=False):
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

    table = yaml.safe_load(open(remote_data,'r'))
    home = get_data_home(data_home=None)
    for name, row in table.items():
        print(name)
        if not full:
            for elem in row:
                print("\t",elem["filename"])
        else:
            for elem in row:
                for key in ["filename", "url", "checksum"]:
                    print("\t{}".format(elem[key]))
                print("\t!downloaded" if exists(join(home,elem["filename"]))
                      else "\tnot downloaded")


#if __name__ == "__main__":
#    import argh
#    parser = argh.ArghParser()
#    parser.add_commands([list_data, load_data])
#    parser.dispatch()

