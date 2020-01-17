"""
IO Code to download datasets
"""

# Parts taken from Scikit-learn
# Copyright (c) 2007 David Cournapeau <cournape@gmail.com>
#               2010 Fabian Pedregosa <fabian.pedregosa@inria.fr>
#               2010 Olivier Grisel <olivier.grisel@ensta.org>
# License: BSD 3 clause

# Christopher Lee 2019

import threading
import hashlib
from os import environ, makedirs
from os.path import dirname, exists, expanduser, isdir, join
from collections import namedtuple
from urllib.request import urlretrieve
from urllib.parse import urlsplit
import sys
import logging

RemoteFileMetadata = namedtuple("RemoteFileMetadata", ["filename", "url", "checksum"])

# Try to import tqdm for a progress bar
try:
    from tqdm import tqdm
except ImportError as e:

    class tqdm(object):
        def __init__(self, total=None):
            self._size = total
            self._seen_so_far = 0

        def update(self, addon):
            self._seen_so_far += addon
            if self._size is None:
                print("Bytes : {}".format(self._seen_so_far))
            else:
                percentage = round((self._seen_so_far / self._size) * 100, 2)
                print("Percentage : {}%".format(percentage))

        def close(self):
            pass


class TransferProgress(object):
    def __init__(self, bucket, filename):
        self._filename = filename
        # self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

        if hasattr(self, "_size"):
            size = self._size
        else:
            size = None
        self._pbar = tqdm(total=size)

    def __call__(self, bytes):
        with self._lock:
            self._seen_so_far += bytes
            self._pbar.update(bytes)
            sys.stdout.flush()

    def __del__(self):
        self._pbar.close()


class DownTransferProgress(TransferProgress):
    def __init__(self, client, bucket, filename):
        self._size = int(
            client.head_object(Bucket=bucket, Key=filename)["ResponseMetadata"][
                "HTTPHeaders"
            ]["content-length"]
        )
        super().__init__(bucket, filename)


class Bunch(dict):
    """Container object for datasets
    Dictionary-like object that exposes its keys as attributes.
    >>> b = Bunch(a=1, b=2)
    >>> b['b']
    2
    >>> b.b
    2
    >>> b.a = 3
    >>> b['a']
    3
    >>> b.c = 6
    >>> b['c']
    6
    """

    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return self.keys()

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setstate__(self, state):
        # Bunch pickles generated with scikit-learn 0.16.* have an non
        # empty __dict__. This causes a surprising behaviour when
        # loading these pickles scikit-learn 0.17: reading bunch.key
        # uses __dict__ but assigning to bunch.key use __setattr__ and
        # only changes bunch['key']. More details can be found at:
        # https://github.com/scikit-learn/scikit-learn/issues/6196.
        # Overriding __setstate__ to be a noop has the effect of
        # ignoring the pickled __dict__
        pass


def get_data_home(data_home=None):
    """Return the path of the mars_data dir.
    This folder is used by some large dataset loaders to avoid downloading the
    data several times.
    By default the data dir is set to a folder named 'mars_data' in the
    user home folder.
    Alternatively, it can be set by the 'MARS_DATA' environment
    variable or programmatically by giving an explicit folder path. The '~'
    symbol is expanded to the user home folder.
    If the folder does not already exist, it is automatically created.
    Parameters
    ----------
    data_home : str | None
        The path to mars_data dir.
    """
    if data_home is None:
        data_home = environ.get("MARS_DATA", join("~", "mars_data"))
    data_home = expanduser(data_home)
    if not exists(data_home):
        logging.info("Creating data directory {}".format(data_home))
        makedirs(data_home)
    return data_home


def clear_data_home(data_home=None):
    """Delete all the content of the data home cache.
    Parameters
    ----------
    data_home : str | None
        The path to mars_data dir.
    """
    data_home = get_data_home(data_home)
    # shutil.rmtree(data_home)


def _sha256(path):
    """Calculate the sha256 hash of the file at path."""
    sha256hash = hashlib.sha256()
    chunk_size = 8192
    with open(path, "rb") as f:
        while True:
            buffer = f.read(chunk_size)
            if not buffer:
                break
            sha256hash.update(buffer)
    return sha256hash.hexdigest()


def _fetch_remote(remote, root=None, stop_on_error=True):
    """Helper function to download a remote dataset into path
    Fetch a dataset pointed by remote's url, save into path using remote's
    filename and ensure its integrity based on the SHA256 Checksum of the
    downloaded file.
    Parameters
    ----------
    remote : RemoteFileMetadata
        Named tuple containing remote dataset meta information: url, filename
        and checksum
    root : string
        Directory to save the file to.
    Returns
    -------
    file_path: string
        Full path of the created file.
    """

    file_path = remote["filename"] if root is None else join(root, remote["filename"])
    dir_path = dirname(file_path)

    if exists(dir_path):
        if not isdir(dir_path):
            raise IOError("Path {} exists and is not a directory".format(dir_path))
    else:
        makedirs(dir_path)

    scheme, location, path, query, fragment = urlsplit(remote["url"])
    print(scheme, location, path)
    if scheme == "s3":
        try:
            from botocore.session import Session
            import boto3
            from botocore.exceptions import NoCredentialsError

            session = Session()
            client = boto3.client("s3")
            progress = DownTransferProgress(client, location, path.lstrip("/"))

            client.download_file(
                location, path.lstrip("/"), file_path, Callback=progress
            )
        except ImportError as e:
            print("Failed to import ", e)
        except NoCredentialsError as e:
            print("No S3 credentials found")

    else:
        urlretrieve(remote["url"], file_path)
    checksum = _sha256(file_path)
    remote["remote_sha256"] = checksum

    if remote["checksum"] != checksum:
        remote["sha256"] = "Failed"
        if stop_on_error:
            raise IOError(
                "{} has an SHA256 checksum ({}) "
                "differing from expected ({}), "
                "file may be corrupted.".format(file_path, checksum, remote["checksum"])
            )
    else:
        remote["sha256"] = "Passed"

    return file_path, remote


def fetch_dataset(
        ARCHIVE,
        data_home=None,
        source_bucket=None,
        download_if_missing=True,
        stop_on_error=True,
):
    """
        Fetch a dataset and return the dataset location
    """

    data_home = get_data_home(data_home=data_home)
    if not exists(data_home):
        makedirs(data_home)
    processed = dict()
    for entry in ARCHIVE:
        logging.info("Getting dataset {}".format(entry["filename"]))
        result = dict()
        ef = entry["filename"]
        entry["filename"] = (
            entry["filename"] if data_home is None else join(data_home, entry["filename"])
        )
        if not exists(entry["filename"]):
            logging.info("Dataset doesn't exist")
            if not download_if_missing:
                logging.info("not downloading")
                processed.get(entry["filename"], dict())["status"] = False
                if stop_on_error:
                    raise IOError("Data not found and `download_if_missing` is False")
            result["status"] = True
            archive_path, remote = _fetch_remote(
                entry, root=None, stop_on_error=stop_on_error
            )
            result["location"] = archive_path
            result["remote_sha256"] = remote["checksum"]
            result["sha256"] = remote["sha256"]
        else:
            result["status"] = True
            result["location"] = entry["filename"]
        processed[ef] = result
    return processed
