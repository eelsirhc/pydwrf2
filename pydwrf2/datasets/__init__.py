from .utils import fetch_dataset, RemoteFileMetadata, Bunch
import pandas as pd

from os.path import dirname, join, exists

def load_data(name):
	module_path = dirname(__file__)
	remote_data = join(module_path, "remote_data.csv")

	df = pd.read_csv(remote_data)
	if any(df["name"]==name):
		data = [v for k,v in df[df["name"]==name].iterrows()]
		return fetch_dataset(data)
	else:
		print(df[df["name"]==name])
		raise NameError("{} not found".format(name))

def list_data(name):
	module_path = dirname(__file__)
	remote_data = join(module_path, "remote_data.csv")
	df = pd.read_csv(remote_data)

	for irow, row in df.iterrows():
			print("{}\t{}\t{}\t{}\t{}".format(row["name"],
									  row["filename"],
									  row["url"],
									  row["checksum"],
									  "downloaded" if exists(row["filename"]) else "not downloaded"
									  ))