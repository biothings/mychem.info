import os

import lxml.html
import numpy as np
import pandas as pd
from biothings import config
from biothings.utils.dataload import dict_convert, dict_sweep

logging = config.logger

VAL_MAP = {"yes": True, "no": False}
process_key = lambda key: key.replace(" ", "_").lower()
process_val = lambda val: VAL_MAP[val] if isinstance(val, str) and val in VAL_MAP.keys() else val
remove_tags = lambda val: (
    lxml.html.document_fromstring(val).text_content() if isinstance(val, str) else val
)
intrs_rename_dict = {
    "Target Ensembl Gene ID": "Ensembl Gene",
    "Target Entrez Gene ID": "Entrez Gene",
    "Target Gene Name": "Symbol",
    "Target Species": "Species",
}


def preprocess_ligands(d: dict):
    """convert key names, remove empty vals and XML tags, and determine _id

    Args:
        d (dict): ligand properties

    Returns:
        dict: processed ligand properties
    """
    if isinstance(d["Synonyms"], str):
        d["Synonyms"] = d["Synonyms"].split("|")
    d = dict_sweep(d, vals=["", np.nan], remove_invalid_list=True)
    d = dict_convert(d, keyfn=process_key)
    d = dict_convert(d, valuefn=process_val)
    d = dict_convert(d, valuefn=remove_tags)

    if "inchikey" in d.keys() and not d["inchikey_dup"]:
        d["_id"] = d["inchikey"]
    elif "pubchem_cid" in d.keys() and not d["cid_dup"]:
        d["_id"] = f"pubchem.compound:{d['pubchem_cid']}"
    elif "pubchem_sid" in d.keys() and not d["sid_dup"]:
        d["_id"] = f"pubchem.substance:{d['pubchem_sid']}"

    for key in ["inchikey_dup", "cid_dup", "sid_dup"]:
        d.pop(key)
    return d


def preprocess_intrs(d: dict):
    """convert key names and remove empty vals, XML tags, and repeated columns

    Args:
        d (dict): interaction properties

    Returns:
        dict: processed interaction properties
    """
    d["Name"] = d["Target"]
    if isinstance(d["Species"], str):
        d["Species"] = d["Species"].lower()

    # redundant since present in ligands
    cols_to_drop = [
        "Ligand ID",
        "CAS Number",
        "Clinical Use Comment",
        "Bioactivity Comment",
        "Ligand Synonyms",
        "Target",
        "Ligand",
        "Type",
        "SMILES",
    ]
    for col in cols_to_drop:
        d.pop(col)

    d = dict_sweep(d, vals=["", np.nan], remove_invalid_list=True)
    d = dict_convert(d, keyfn=process_key)
    d = dict_convert(d, valuefn=remove_tags)
    return d


def load_ligands(data_folder: str):
    # pk: Ligand ID,Target ID,Target Ligand ID,Target Species
    # inner join of primary_targets_csv[pk] and detailed_csv[pk] is primary_targets_csv[pk]
    interactions_file = os.path.join(data_folder, "approved_drug_detailed_interactions.csv")
    ligands_file = os.path.join(data_folder, "ligands.csv")
    assert os.path.exists(interactions_file) and os.path.exists(ligands_file)

    ligands = pd.read_csv(ligands_file, skiprows=1, dtype=object).set_index("Ligand ID")
    interactions = (
        pd.read_csv(interactions_file, skiprows=1, dtype=object)
        .rename(intrs_rename_dict, axis=1)
        .to_dict(orient="records")
    )
    assert type(list(ligands.keys())[0]) == str

    # keep track of duplicates for determining _id
    ligands["inchikey_dup"] = ligands["InChIKey"].duplicated()
    ligands["cid_dup"] = ligands["PubChem CID"].duplicated()
    ligands["sid_dup"] = ligands["PubChem SID"].duplicated()
    ligands = ligands.to_dict(orient="index")

    for row in interactions:
        ligand_id = str(row["Ligand ID"])

        # NOTE: we assume ligand IDs in interactions will be found in ligands
        if "interaction_targets" not in ligands[ligand_id].keys():
            ligands[ligand_id]["interaction_targets"] = []
            ligands[ligand_id]["CAS Number"] = row["CAS Number"]
            ligands[ligand_id]["Clinical Use Comment"] = row["Clinical Use Comment"]
            ligands[ligand_id]["Bioactivity Comment"] = row["Bioactivity Comment"]

        ligands[ligand_id]["interaction_targets"].append(preprocess_intrs(row))

    for k, ligand in ligands.items():
        ligand["_id"] = f"gtopdb:{k}"  # default _id if others are NaN or duplicated
        yield preprocess_ligands(ligand)
