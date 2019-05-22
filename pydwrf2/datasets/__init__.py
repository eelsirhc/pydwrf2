from .utils import fetch_dataset
import pandas as pd

ARCHIVE = RemoteFileMetadata(
    filename='cal_housing.tgz',
    url='https://ndownloader.figshare.com/files/5976036',
    checksum=('aaa5c9a6afe2225cc2aed2723682ae40'
              '3280c4a3695a2ddda4ffb5d8215ea681'))

from os import dirname, join

def load_data(name):

	module_path = dirname(__file__)
	remote_data = join(module_path, "remote_data.csv")

	df = pd.read_csv(remote_data)

	return load_data(df[df["name"]==name])
