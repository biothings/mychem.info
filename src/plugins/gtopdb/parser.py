import os

import lxml.html
import numpy as np
import pandas as pd
from biothings import config
from biothings.utils.dataload import dict_convert, dict_sweep

logging = config.logger

VAL_MAP = {"yes": True, "no": False}
def process_key(key): return key.replace(" ", "_").lower()


def process_val(val): return (
    VAL_MAP[val] if isinstance(val, str) and val in VAL_MAP.keys() else val
)


def remove_tags(val): return (
    lxml.html.document_fromstring(
        val).text_content() if isinstance(val, str) else val
)


intrs_rename_dict = {
    "Target Ensembl Gene ID": "Ensembl Gene",
    "Target Entrez Gene ID": "Entrez Gene",
    "Target Gene Name": "Symbol",
    "Target Species": "Species",
}
recognized_code_systems = [
    "cas",
    "pubchem_cid",
    "pubchem_sid",
    "uniprot_id",
    "ensembl_id",
]


def preprocess_ligands(d: dict, _id: str):
    """convert key names, remove empty vals and XML tags, and determine _id

    Args:
        d (dict): ligand properties
        _id (str): default _id

    Returns:
        Tuple[dict, str]: processed ligand properties, and _id
    """

    d = dict_sweep(d, vals=["", np.nan], remove_invalid_list=True)
    d = dict_convert(d, keyfn=process_key)
    d = dict_convert(d, valuefn=process_val)
    d = dict_convert(d, valuefn=remove_tags)

    if "inchikey" in d.keys() and not d["inchikey_dup"]:
        _id = d["inchikey"]
    elif "pubchem_cid" in d.keys() and not d["cid_dup"]:
        _id = d['pubchem_cid']
    elif "pubchem_sid" in d.keys() and not d["sid_dup"]:
        _id = d['pubchem_sid']

    for key in ["inchikey_dup", "cid_dup", "sid_dup"]:
        d.pop(key)

    if "cas_number" in d.keys():
        d["cas"] = d.pop("cas_number")

    if "type" in d.keys():
        d["type"] = d["type"].lower()
    if "species" in d.keys():
        species_list = d["species"].split(", ")
        d["species"] = [species.lower() for species in species_list]

    if "synonyms" in d.keys():
        d["synonyms"] = d["synonyms"].split("|")
    if "uniprot_id" in d.keys():
        d["uniprot_id"] = d["uniprot_id"].split("|")
    if "ensembl_id" in d.keys():
        d["ensembl_id"] = d["ensembl_id"].split("|")

    xrefs = parse_xrefs(d)
    if len(xrefs) > 0:
        d["xrefs"] = xrefs

    return d, _id


def preprocess_intrs(d: dict):
    """convert key names and remove empty vals, XML tags, and repeated columns

    Args:
        d (dict): interaction properties

    Returns:
        dict: processed interaction properties
    """
    d["Name"] = d["Target"]

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

    d = dict_convert(d, keyfn=process_key)
    d = dict_convert(d, valuefn=remove_tags)
    d = dict_sweep(d, vals=["", np.nan], remove_invalid_list=True)
    return d


def parse_xrefs(d: dict):
    xrefs = {}
    for k in recognized_code_systems:
        new_k = k
        if k in d.keys():
            if k == "uniprot_id":
                new_k = "uniprotkb"
            elif k == "ensembl_id":
                new_k = "ensembl"

            xrefs[new_k] = d[k]
            d.pop(k)
    return xrefs


def load_ligands(data_folder: str):
    # pk: Ligand ID,Target ID,Target Ligand ID,Target Species
    # inner join of primary_targets_csv[pk] and detailed_csv[pk] is primary_targets_csv[pk]
    interactions_file = os.path.join(
        data_folder, "approved_drug_detailed_interactions.csv"
    )
    ligands_file = os.path.join(data_folder, "ligands.csv")
    assert os.path.exists(interactions_file) and os.path.exists(ligands_file)

    ligands = pd.read_csv(ligands_file, skiprows=1,
                          dtype=object).set_index("Ligand ID")
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
        # default _id uses `ligand_id` if others are NaN or duplicated
        ligand["ligand_id"] = k
        ligand, _id = preprocess_ligands(ligand, k)
        if "interaction_targets" in ligand:
            ligand["no_of_interaction_targets"] = len(
                ligand["interaction_targets"])
        yield {"_id": _id, "gtopdb": ligand}
