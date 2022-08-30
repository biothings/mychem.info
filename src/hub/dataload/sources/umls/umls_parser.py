import os
import time
from collections import defaultdict

from biothings_client import get_client

CHEM_CLIENT = get_client('chem')
# list of UMLS semantic types belonging to chemical is based on
# https://www.nlm.nih.gov/research/umls/META3_current_semantic_types.html
UMLS_CHEMICAL_SEMANTIC_TYPES = [
    "Manufactured Object",
    "Medical Device",
    "Drug Delivery Device",
    "Research Device",
    "Clinical Drug",
    'Substance',
    'Chemical',
    'Chemical Viewed Functionally',
    'Pharmacologic Substance',
    'Antibiotic',
    'Biomedical or Dental Material',
    'Biologically Active Substance',
    'Hormone',
    'Enzyme',
    'Vitamin',
    'Immunologic Factor',
    'Receptor',
    'Indicator, Reagent, or Diagnostic Acid',
    'Hazardous or Poisonous Substance',
    'Organic Chemical',
    'Nucleic Acid, Nucleoside, or Nucleotide',
    'Amino Acid, Peptide, or Protein',
    'Inorganic Chemical',
    'Element, Ion, or Isotope',
    'Body Substance',
    'Food'
]


def fetch_chemical_umls_cuis(mrsty_file):
    """Fetch all UMLS CUI IDs belonging to chemical semantic types

    :param: mrsty_file: the file path of MRSTY.RRF file
    """
    chem_set = set()
    with open(mrsty_file, "r") as fin:
        for line in fin:
            vals = line.rstrip("\n").split("|")
            if vals[3] in UMLS_CHEMICAL_SEMANTIC_TYPES:
                chem_set.add(vals[0])
    return chem_set


def query_mesh(mesh_ids: list) -> dict:
    """Use biothings_client.py to query mesh ids and get back '_id' in mychem.info

    :param: mesh_ids: list of mesh ids
    """
    res = CHEM_CLIENT.querymany(
        mesh_ids, scopes='drugcentral.xrefs.mesh_supplemental_record_ui,ginas.xrefs.MESH,pharmgkb.xrefs.mesh', fields='_id')
    new_res = defaultdict(list)
    for item in res:
        if not "notfound" in item:
            new_res[item['query']].append(item['_id'])
    return new_res


def query_drug_name(names: list) -> dict:
    """Use biothings_client.py to query drug names and get back '_id' in mychem.info

    :param: names: list of drug names
    """
    new_res = defaultdict(list)
    n = 500
    for i in range((len(names) + n - 1) // n):
        print(i)
        try:
            res = CHEM_CLIENT.querymany(
                names[i * n:(i + 1) * n], scopes='ginas.preferred_name, pharmgkb.name, chebi.name, chembl.pref_name, drugbank.name', fields='_id')
        except:
            print("failed at {}".format(i))
            continue
        for item in res:
            if not item.get("notfound"):
                new_res[item['query']].append(item['_id'])
    return new_res


def parse_umls(rrf_file, chem_umls):
    """Parse the UMLS to determine the HGNC identifier of each gene CUI.
    The relevant files are in the archive <version>-1-meta.nlm (a zip file)
    within <version>/META/MRCONSO.RRF.*.gz
    Concatenate the unzipped versions of the MRCONSO files together to get the
    final MRCONSO.RRF file, which is a | delimited text file without a header.
    """

    res = defaultdict(list)
    mesh_ids = set()
    names = set()
    with open(rrf_file, "r") as fin:
        for line in fin:
            if "|MSH|" in line:
                vals = line.rstrip("\n").split("|")
                cui = vals[0]
                if cui in chem_umls:
                    if vals[1] == 'ENG' and vals[2] == 'P':
                        mesh_id = vals[vals.index('MSH') - 1]
                        res[cui].append({'cui': cui,
                                         'mesh': mesh_id,
                                         'name': vals[-5]})
                        mesh_ids.add(mesh_id)
                        if ',' not in vals[-5]:
                            names.add('"' + vals[-5] + '"')
    return (res, list(mesh_ids), list(names))


def unlist(l):
    l = list(l)
    if len(l) == 1:
        return l[0]
    return l


def load_data(data_folder):
    mrsat_file = os.path.join(data_folder, 'MRSTY.RRF')
    mrconso_file = os.path.join(data_folder, 'MRCONSO.RRF')
    if not os.path.exists(mrsat_file):
        raise FileNotFoundError(
            """Could not find 'MRSTY.RRF' in {}.
            Please download UMLS Metathesaurus files manually and extract to folder.
            """.format(data_folder))
    if not os.path.exists(mrconso_file):
        raise FileNotFoundError(
            """Could not find 'MRCONSO.RRF' in {}.
            Please download manually and extract to folder.""".format(data_folder))
    chem_umls = fetch_chemical_umls_cuis(mrsat_file)
    cui_map, mesh_ids, names = parse_umls(mrconso_file, chem_umls)
    name_mapping = query_drug_name(names)
    time.sleep(200)
    mesh_id_mapping = query_mesh(mesh_ids)
    res = []
    id_set = set()
    for cui, info in cui_map.items():
        found = False
        for rec in info:
            mesh = rec.get('mesh')
            if mesh_id_mapping.get(mesh):
                for _id in mesh_id_mapping.get(mesh):
                    if _id not in id_set:
                        res.append({
                            "_id": _id,
                            "umls": rec
                        })
                        id_set.add(_id)
                        found = True
                continue
            name = rec.get("name")
            if name_mapping.get(name):
                for _id in name_mapping.get(name):
                    if _id not in id_set:
                        res.append({
                            "_id": _id,
                            "umls": rec
                        })
                        id_set.add(_id)
                        found = True
                continue
        if not found:
            new_info = {
                "cui": unlist([item['cui'] for item in info]),
                'mesh': unlist([item['mesh'] for item in info]),
                'name': unlist([item['name'] for item in info])
            }
            if cui not in id_set:
                res.append({
                    "_id": cui,
                    "umls": new_info
                })
                id_set.add(cui)
    return res


if __name__ == "__main__":
    import json
    import sys

    # Add config directory to path
    sys.path.append("../../../../")

    from umls_dump import UMLSDumper

    dumper = UMLSDumper()
    dumper.get_latest_release()
    dumper.create_todump_list()

    for rec in load_data(dumper.new_data_folder):
        print(json.dumps(rec, indent=2))
