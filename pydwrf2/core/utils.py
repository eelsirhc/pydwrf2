import os


def add_prefix_to_filename(filename, prefix):
    """Adds a prefix to the filename, including path."""
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    return os.path.join(dirname, prefix + basename)
