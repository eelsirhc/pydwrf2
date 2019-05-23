import os
import numpy as np
from contextlib import contextmanager
import xarray

def add_prefix_to_filename(filename, prefix):
    """Adds a prefix to the filename, including path."""
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    return os.path.join(dirname, prefix + basename)


@contextmanager
def open_dataset(fh,aggdim="Time"):
    """opens a file if the name is supplied, or transparently returns a filehandle"""
    if isinstance(fh,str):
        try: 
            ff=xarray.open_dataset(fh)
            yield ff
        finally:
            ff.close()
    elif isinstance(fh,list):
        try:
            ff=xarray.open_mfdataset(fh,aggdim="Time")
            yield ff
        finally:
            ff.close()
        yield fh
    elif isinstance(fh,xarray.Dataset):
        yield fh
    else:
        raise Exception("No filename or filehandle given {0}".format(fh))
    
