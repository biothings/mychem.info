import os.path
import json


def load_data(data_folder):
    infile = os.path.join(data_folder,"data.json")
    with open(infile) as f:
        data = json.load(f)
    for doc in data:
        yield doc


