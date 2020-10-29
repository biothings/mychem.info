from collections import defaultdict
from biothings_client import get_client
import os
import copy
import time
import json

CHEM_CLIENT = get_client('chem')


def fetch_cohd2ids(doc):
    """Fetch all UMLS CUI IDs belonging to chemical semantic types

    :param: mrsty_file: the file path of MRSTY.RRF file
    """
    chembl_mapping = defaultdict(set)
    pubchem_mapping = defaultdict(set)
    chebi_mapping = defaultdict(set)
    cohdid2name_mapping = {}
    for rec in doc:
        if rec["domain_id"] == "Drug" and rec["xrefs"]:
            cohdid2name_mapping[rec["_id"]] = rec["concept_name"]
            if "chebi" in rec["xrefs"]:
                if isinstance(rec["xrefs"]["chebi"], str):
                    chebi_mapping[rec["xrefs"]["chebi"]].add(rec["_id"])
                elif isinstance(rec["xrefs"]["chebi"], list):
                    for chebi in rec["xrefs"]["chebi"]:
                        chebi_mapping[chebi].add(rec["_id"])
            if "chembl" in rec["xrefs"]:
                if isinstance(rec["xrefs"]["chembl"], str):
                    chembl_mapping[rec["xrefs"]["chembl"]].add(rec["_id"])
                elif isinstance(rec["xrefs"]["chembl"], list):
                    for chembl in rec["xrefs"]["chembl"]:
                        chembl_mapping[chembl].add(rec["_id"])
            if "pubchem" in rec["xrefs"]:
                if isinstance(rec["xrefs"]["pubchem"], str):
                    pubchem_mapping[rec["xrefs"]["pubchem"]].add(rec["_id"])
                elif isinstance(rec["xrefs"]["pubchem"], list):
                    for pubchem in rec["xrefs"]["pubchem"]:
                        pubchem_mapping[pubchem].add(rec["_id"])
    return {"chembl": chembl_mapping, "chebi": chebi_mapping, "pubchem": pubchem_mapping, "cohd": cohdid2name_mapping}


def query_chembl(chembl_ids: list) -> dict:
    """Use biothings_client.py to query mesh ids and get back '_id' in mychem.info

    :param: chembl_ids: list of chembl ids
    """
    res = CHEM_CLIENT.querymany(
        chembl_ids, scopes='chembl.molecule_chembl_id', fields='_id')
    new_res = defaultdict(set)
    for item in res:
        if not "notfound" in item:
            new_res[item['_id']].add(item['query'])
    return new_res


def query_chebi(chebi_ids: list) -> dict:
    """Use biothings_client.py to query mesh ids and get back '_id' in mychem.info

    :param: chebi_ids: list of chebi ids
    """
    res = CHEM_CLIENT.querymany(
        chebi_ids, scopes='chebi.id,chembl.chebi_par_id', fields='_id')
    new_res = defaultdict(set)
    for item in res:
        if not "notfound" in item:
            new_res[item['_id']].add(item['query'])
    return new_res


def query_pubchem(pubchem_ids: list) -> dict:
    """Use biothings_client.py to query mesh ids and get back '_id' in mychem.info

    :param: pubchem_ids: list of pubchem ids
    """
    res = CHEM_CLIENT.querymany(
        pubchem_ids, scopes='pubchem.cid,drugbank.xrefs.pubchem.cid', fields='_id')
    new_res = defaultdict(set)
    for item in res:
        if not "notfound" in item:
            new_res[item['_id']].add(int(item['query']))
    return new_res


def load_data():
    import requests
    cohd_file = requests.get(
        "https://raw.githubusercontent.com/polyg314/COHD_APIs/master/COHD_prework/concept_xref.json").json()
    mychem2cohd_mapping = defaultdict(set)
    cohd_mapping = fetch_cohd2ids(cohd_file)
    chembl2mychem = query_chembl(cohd_mapping["chembl"].keys())
    pubchem2mychem = query_pubchem(cohd_mapping["pubchem"].keys())
    chebi2mychem = query_chebi(cohd_mapping["chebi"].keys())
    for _id in chembl2mychem:
        for chembl in chembl2mychem[_id]:
            for cohd in cohd_mapping["chembl"][chembl]:
                mychem2cohd_mapping[_id].add(cohd)
        for chebi in chebi2mychem[_id]:
            for cohd in cohd_mapping["chebi"][chebi]:
                mychem2cohd_mapping[_id].add(cohd)
        for pubchem in chebi2mychem[_id]:
            for cohd in cohd_mapping["pubchem"][pubchem]:
                mychem2cohd_mapping[_id].add(cohd)
    for k, v in mychem2cohd_mapping.items():
        cohd = [{"omop": item, "name": cohd_mapping["cohd"][item]}
                for item in v]
        if len(cohd) == 1:
            cohd = cohd[0]
        yield {
            "_id": k,
            "omop": cohd
        }
