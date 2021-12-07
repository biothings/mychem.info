import pandas as pd
from collections import defaultdict
from biothings.utils.dataload import dict_sweep, unlist
import json
import requests

from . import file_path_pharma_class, file_path_faers, file_path_act, file_path_omop, file_path_approval, file_path_drug_dosage, file_path_structure, file_path_identifier,file_path_synonym

def process_pharmacology_action(file_path_pharma_class):
    df_drugcentral_pharma_class = pd.read_csv(file_path_pharma_class, sep=",", names=['_id', 'struc_id', 'role', 'description', 'code', 'source'])
    df_drugcentral_pharma_class['source_name'] = df_drugcentral_pharma_class.apply(lambda row: row.source + '_' + row.role, axis=1)
    df_drugcentral_pharma_class = df_drugcentral_pharma_class.where((pd.notnull(df_drugcentral_pharma_class)), None)
    d = []
    for strucid, subdf in df_drugcentral_pharma_class.groupby('struc_id'):
        records = subdf.to_dict(orient="records")
        pharm_class_related = defaultdict(list)
        for _record in records:
            pharm_class_related[_record['source_name'].lower().replace("chebi_has role", "chebi")].append({'description': _record['description'], 'code': _record['code']})
        drecord = {"_id": strucid, "pharmacology_class": pharm_class_related}
        d.append(drecord)
    return {x['_id']: x['pharmacology_class'] for x in d}

def process_faers(file_path_faers):
    """
    # TODO: JSON field naming needs to be confirmed
    """
    df_drugcentral_faers = pd.read_csv(file_path_faers, sep=",", names=['_id', 'struc_id', 'meddra_term', 'meddra_code', 'level', 'llr', 'llr_threshold', 'drug_ae', 'drug_no_ae', 'no_drug_ae', 'no_drug_no_ar'])
    df_drugcentral_faers = df_drugcentral_faers.where((pd.notnull(df_drugcentral_faers)), None)    
    d = []
    for strucid, subdf in df_drugcentral_faers.groupby('struc_id'):
        records = subdf.to_dict(orient="records")
        faers_related = [{k: v for k, v in record.items() if k not in {'struc_id', '_id'}} for record in records]
        drecord = {"_id": strucid, "fda_adverse_event": faers_related}
        d.append(drecord)
    return {x['_id']: x['fda_adverse_event'] for x in d}

def process_act(file_path_act):
    df_drugcentral_act = pd.read_csv(file_path_act, sep=",", names=["act_id", "struct_id", "target_id", "target_name", "target_class", "accession", "gene", "swissprot", "act_value", "act_unit", "act_type", "act_comment", "act_source", "relation", "moa", "moa_source", "act_source_url", "moa_source_url", "action_type", "first_in_class", "tdl", "act_ref_id", "moa_ref_id", "organism"])
    df_drugcentral_act = df_drugcentral_act.where((pd.notnull(df_drugcentral_act)), None)
    d = []
    for strucid, subdf in df_drugcentral_act.groupby('struct_id'):
        records = subdf.to_dict(orient="records")
        pharm_class_related = []
        for _record in records:
            _summary = {'uniprot': []}
            if _record['accession']:
                accession = _record['accession'].split('|')
            else:
                accession = [None for i in range(10)]
            if _record['gene']:
                gene = _record['gene'].split('|')
            else:
                gene = [None for i in range(10)]
            if _record['swissprot']:
                swissprot = _record['swissprot'].split('|')
            else:
                swissprot = [None for i in range(10)]
            if not len(accession) == len(gene) == len(swissprot):
                continue
            for i in range(len(accession)):
                _summary['uniprot'].append({'uniprot_id': accession[i], 'gene_symbol': gene[i], 'swissprot_entry': swissprot[i]})
            for k, v in _record.items():
                if k not in ['uniprot', 'act_id', 'struct_id', 'target_id', 'accession', 'gene', 'swissprot', 'tdl', 'act_comment', "act_source_url", "moa_source_url", 'relation', "act_ref_id", "moa_ref_id", 'first_in_class']:
                    _summary[k] = v
            pharm_class_related.append(_summary)
        drecord = {"_id": strucid, "bioactivity": pharm_class_related}
        d.append(drecord)
    return {x['_id']: x['bioactivity'] for x in d}

def process_omop(file_path_omop):
    df_drugcentral_omop = pd.read_csv(file_path_omop, sep=",", names=['_id', 'struct_id', 'concept_id', 'relationship_name', 'concept_name', 'umls_cui', 'snomed_full_name', 'cui_semantic_type', 'snomed_conceptid'])
    df_drugcentral_omop = df_drugcentral_omop.where((pd.notnull(df_drugcentral_omop)), None)
    d = []
    for strucid, subdf in df_drugcentral_omop.groupby('struct_id'):
        records = subdf.to_dict(orient="records")
        omop_related = defaultdict(list)
        for _record in records:
            if _record['snomed_conceptid']:
                _record['snomed_conceptid'] = int(_record['snomed_conceptid'])
            omop_related[_record['relationship_name'].lower().replace('-', '_').replace(' ', '_')].append({'umls_cui': _record['umls_cui'], 'concept_name': _record['concept_name'], 'snomed_full_name': _record['snomed_full_name'], 'cui_semantic_type': _record['cui_semantic_type'], 'snomed_concept_id': _record['snomed_conceptid']})
        drecord = {"_id": strucid, "drug_use": omop_related}
        d.append(drecord)
    return {x['_id']: x['drug_use'] for x in d}

def process_approval(file_path_approval):
    df_drugcentral_approval = pd.read_csv(file_path_approval, sep=",", names=['_id', 'struct_id', 'date', 'agency', 'company', 'orphan'])
    df_drugcentral_approval = df_drugcentral_approval.where((pd.notnull(df_drugcentral_approval)), None)
    d = []
    for strucid, subdf in df_drugcentral_approval.groupby('struct_id'):
        records = subdf.to_dict(orient="records")
        approval_related = [{k: v for k, v in record.items() if k not in {'struct_id', '_id'}} for record in records]
        drecord = {"_id": strucid, "approval": approval_related}
        d.append(drecord)
    return {x['_id']: x['approval'] for x in d}

def process_drug_dosage(file_path_drug_dosage):
    df_drugcentral_drug_dosage = pd.read_csv(file_path_drug_dosage, sep=",", names=['_id', 'atc_code', 'dosage', 'unit', 'route', 'comment', 'struct_id'])
    df_drugcentral_drug_dosage = df_drugcentral_drug_dosage.where((pd.notnull(df_drugcentral_drug_dosage)), None)
    d = []
    for strucid, subdf in df_drugcentral_drug_dosage.groupby('struct_id'):
        records = subdf.to_dict(orient="records")
        drug_dosage_related = [{k: v for k, v in record.items() if k not in {'struct_id', '_id', 'atc_code', 'comment'}} for record in records]
        drecord = {"_id": strucid, "drug_dosage": drug_dosage_related}
        d.append(drecord)
    return {x['_id']: x['drug_dosage'] for x in d}


def process_synonym(file_path_synonym):
    df_drugcentral_synonym = pd.read_csv(file_path_synonym, sep=",", names=["_id", "struct_id", 'synonym', 'pref', 'parent', 's2'])
    df_drugcentral_synonym = df_drugcentral_synonym.where((pd.notnull(df_drugcentral_synonym)), None)
    d = []
    for strucid, subdf in df_drugcentral_synonym.groupby('struct_id'):
        records = subdf.to_dict(orient="records")
        synonym_related = []
        for record in records:
            for k, v in record.items():
                if k not in {'struct_id', '_id', 'pref', 'parent', 's2'}:
                    synonym_related.append(v)
        drecord = {"_id": strucid, "synonyms": synonym_related}
        d.append(drecord)
    return {x['_id']: x['synonyms'] for x in d}

def process_structure(file_path_structure):
    df_drugcentral_structure = pd.read_csv(file_path_structure, sep="\t")
    df_drugcentral_structure = df_drugcentral_structure.where((pd.notnull(df_drugcentral_structure)), None)
    d = []
    for strucid, subdf in df_drugcentral_structure.groupby('ID'):
        records = subdf.to_dict(orient="records")
        drug_dosage_related = [{k.lower(): v for k, v in record.items() if k not in {'ID'}} for record in records]
        drecord = {"_id": strucid, "structures": drug_dosage_related[0]}
        d.append(drecord)
    return {x['_id']: x['structures'] for x in d}

def process_identifier(file_path_identifier):
    df_drugcentral_identifier = pd.read_csv(file_path_identifier, sep=",", names=["_id", "identifier", "id_type", "struct_id", "parent"])
    df_drugcentral_identifier = df_drugcentral_identifier.where((pd.notnull(df_drugcentral_identifier)), None)
    d = []
    for strucid, subdf in df_drugcentral_identifier.groupby('struct_id'):
        records = subdf.to_dict(orient="records")
        identifier_related = defaultdict(list)
        for _record in records:
            identifier_related[_record['id_type'].lower()].append(_record['identifier'])             
        drecord = {"_id": strucid, "external_ref": identifier_related}
        d.append(drecord)
    return {x['_id']: x['external_ref'] for x in d}

def to_list(_key):
    if type(_key) != list:
        return [_key]
    else:
        return _key

def xrefs_2_inchikey(xrefs_dict):
    xrefs_key_list = ['unii', 'drugbank_id', 'chembl_id', 'chebi', 'pubchem_cid']
    mychem_filed_dict = {'unii': 'unii.unii:', 'chebi': 'chebi.chebi_id:"', 'pubchem_cid': 'pubchem.cid:"CID','chembl_id': 'chembl.molecule_chembl_id:"', 'drugbank_id': 'drugbank.accession_number:"'}
    mychem_query = 'http://mychem.info/v1/query?q='
    result = None
    for _key in xrefs_key_list:
        if _key in xrefs_dict:
            for _xrefs in to_list(xrefs_dict[_key]):
                query_url = mychem_query + mychem_filed_dict[_key] + _xrefs + '"'
                json_doc = requests.get(query_url).json()
                if 'hits' in json_doc and json_doc['hits']:
                    if len(json_doc['hits']) == 1:
                        result = json_doc['hits'][0]['_id']
                    else:
                        result = json_doc['hits'][0]['_id']
    return result

def load_data():
    pharmacology_class = process_pharmacology_action(file_path_pharma_class)
    faers = process_faers(file_path_faers)
    act = process_act(file_path_act)
    omop = process_omop(file_path_omop)
    approval = process_approval(file_path_approval)
    drug_dosage = process_drug_dosage(file_path_drug_dosage)
    synonyms = process_synonym(file_path_synonym)
    structures = process_structure(file_path_structure)
    identifiers = process_identifier(file_path_identifier)
    for struc_id in set(list(pharmacology_class.keys()) + list(faers.keys()) + list(act.keys()) + list(omop.keys()) + list(approval.keys()) + list(drug_dosage.keys()) + list(identifiers.keys()) + list(synonyms.keys()) + list(structures.keys())):
    #for disease_id in set(list(d_go_bp.keys()) + list(d_go_mf.keys()) + list(d_go_cc.keys()) + list(d_pathway.keys())):
        if structures.get(struc_id, {}).get('inchikey', {}):
            _doc = {
                '_id': structures.get(struc_id, {}).get('inchikey', {}),
                'drugcentral': {
                    "pharmacology_class": pharmacology_class.get(struc_id, {}),
                    "fda_adverse_event": faers.get(struc_id, {}),
                    "bioactivity": act.get(struc_id, {}),
                    "drug_use": omop.get(struc_id, {}),
                    "approval": approval.get(struc_id, {}),
                    "drug_dosage": drug_dosage.get(struc_id, {}),
                    "synonyms": synonyms.get(struc_id, {}),
                    "structures": structures.get(struc_id, {}),
                    "xrefs": identifiers.get(struc_id, {})
                }
            }
        else:
            _id = xrefs_2_inchikey(identifiers.get(struc_id, {}))
            if not _id:
                _id = 'DrugCentral:' + str(struc_id)
            _doc = {
                '_id': _id,
                'drugcentral': {
                    "pharmacology_class": pharmacology_class.get(struc_id, {}),
                    "fda_adverse_event": faers.get(struc_id, {}),
                    "bioactivity": act.get(struc_id, {}),
                    "drug_use": omop.get(struc_id, {}),
                    "approval": approval.get(struc_id, {}),
                    "drug_dosage": drug_dosage.get(struc_id, {}),
                    "synonyms": synonyms.get(struc_id, {}),
                    "structures": structures.get(struc_id, {}),
                    "xrefs": identifiers.get(struc_id, {})
                }
            }
        _doc = (dict_sweep(unlist(_doc), [None]))
        yield _doc


