# Parse DrugBank's XML file to map obsolete DB IDs

import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd

def map_dbids(fname):
    """Parse the DrugBank XML to determine obsolete DrugBank ID mappings to the
    current DrugBank ID."""

    tree = ET.parse(fname)
    root = tree.getroot()

    namespace = {"DB": "http://www.drugbank.ca"}

    DB_ID_LEN = 7

    res = defaultdict(list)
    for drug in root.iterfind("DB:drug", namespace):
        primary_id = drug.find("DB:drugbank-id[@primary='true']", namespace).text
        assert primary_id.startswith("DB")

        for uid in drug.iterfind("DB:drugbank-id", namespace):
            id_val = uid.text

            if id_val.startswith("DB") and len(id_val) == DB_ID_LEN:
                res["primary_id"].append(primary_id)
                res["other_id"].append(id_val)

    return pd.DataFrame(res).drop_duplicates()
