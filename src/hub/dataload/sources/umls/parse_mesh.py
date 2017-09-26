# Parse the MeSH source files for MeSH id to UNII mappings
# Works for both desc and supp XML files

import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd

def parse_file(fname):
    """Parse XML version of MeSH (desc and supp files) to give MeSH ID to
    UNII mappings."""

    def cleanup(df):
        """Filter to only concepts mappable to UNIIs.

        Main types of identifiers seem to be:
            1. "0" for empty fields (seem to be categories/families of
                chemicals, which by definition do not have specific InChIKeys or
                structures, so we can safely ignore these).
            2. Things with "EC" numbers, which seem to be enzymes/gene products,
                which we can also skip.
            3. UNIIs, which are of length 10 and are uniquely mappable to InChIKeys
            4. CAS numbers, which are less useful for converting to InChIKey.

        At the moment only the UNIIs are kept.
        """
        return (df
            .assign(
                isunii = lambda df: df["uid"].str.match(r'^[A-Z0-9]{10}$')
            )
            .query("isunii")
            .drop("isunii", axis=1)
            .rename(columns={"uid": "unii"})
        )

    assert fname.endswith(".xml"), "File must be XML"
    assert "desc" in fname or "supp" in fname, "Wrong files given"

    # which tags to search for in the XML file
    record = "{}Record".format(
        "Descriptor" if "desc" in fname else "Supplemental"
    )
    record_ui = "{}UI".format(
        "Descriptor" if "desc" in fname else "SupplementalRecord"
    )

    tree = ET.parse(fname)
    root = tree.getroot()

    res = defaultdict(list)
    for concept in root.iterfind(record):
        mesh_id = concept.find(record_ui).text

        node = concept.find("ConceptList/Concept/RegistryNumber")
        if node is not None:
            res["mesh_id"].append(mesh_id)
            res["uid"].append(node.text)

    return cleanup(pd.DataFrame(res))
