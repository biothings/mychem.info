from collections import defaultdict

import pandas as pd

from parse_mesh import parse_file
from parse_drugbank import map_dbids

def read_umls(fname):
    """Read through MRCONSO.RRF and extract relevant info.

    Currently extracted information:
        1. DrugBank ID
        2. MeSH ID
        3. UNII

    Other data sources could be processed here, but diminishing returns kick
    in very quickly (they provide redundant data).

    For example, RxNorm mappings are almost a complete subset of the direct
    UNII mappings.

    Returns a pandas DataFrame with three columns.
    """
    res = defaultdict(list)
    with open(fname, "r") as fin:
        for line in fin:
            vals = line.rstrip("\n").split("|")

            cui, sab, code = vals[0], vals[11], vals[13]

            if sab in {"DRUGBANK", "MSH", "MTHSPL", "NCI_FDA"}:
                res["cui"].append(cui)
                res["code"].append(code)
                res["source"].append(sab)

    return pd.DataFrame(res).drop_duplicates()

def format_data(df, key, val):
    """Format a two column result dataframe for output."""

    return {
        group: set(data[val])
        for group, data in df.groupby(key)
    }

def load_data():

    info = read_umls("data/MRCONSO.RRF")

#-------------------------------------------------------------------------------

    # some of the drugbank ids given in the UMLS are obsolete
    # we need to map them to their current values

    drugbank = (info
        .query("source == 'DRUGBANK'")
        .drop("source", axis=1)
        .merge(
            map_dbids("data/drugbank_full.xml"),
            how="inner", left_on="code", right_on="other_id"
        )
        [["cui", "primary_id"]]
        .rename(columns={"primary_id": "drugbank_id"})
        .drop_duplicates()
    )

#-------------------------------------------------------------------------------

    # direct CUI to UNII mappings are processed here

    uniis = (info
        .query("source in('MTHSPL', 'NCI_FDA')")
        .assign(isunii = lambda df: df["code"].str.match(r'^[A-Z0-9]{10}$'))
        .query("isunii")
        [["cui", "code"]]
        .rename(columns={"code": "unii"})
        .drop_duplicates()
    )

#-------------------------------------------------------------------------------

    # CUI to MeSH to UNII

    mesh_uniis = (parse_file("data/desc2017.xml")
        .append(parse_file("data/supp2017.xml"))
        .merge(
            info.query("source == 'MSH'"),
            how="inner", left_on="mesh_id", right_on="code"
        )
        [["cui", "unii"]]
        .drop_duplicates()
    )

#-------------------------------------------------------------------------------

    # yield drugbank results
    for key, val in format_data(drugbank, "drugbank_id", "cui"):
        yield {
            "_id": key, # drugbank_id
            "umls": {
                "cuis": val # a set of UMLS CUIs
            }
        }

    # yield UNII results
    for key, val in format_data(uniis.append(mesh_uniis), "unii", "cui"):
        yield {
            "_id": key, # UNII
            "umls": {
                "cuis": val # a set of UMLS CUIs
            }
        }
