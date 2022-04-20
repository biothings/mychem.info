"""
    Mychem.info
    https://mychem.info/
    Chemical and Drug Annotation as a Service.
"""

import re

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'localhost:9200'
ES_INDICES = {
    "chem": "mychem_current",
    "drug": "mychem_current",
    "compound": "mychem_current"
}
ES_SCROLL_TIME = '10m'

# *****************************************************************************
# Endpoint Specifics
# *****************************************************************************

ANNOTATION_ID_REGEX_LIST = [
    (re.compile(r'((chembl\:(?P<term>chembl[0-9]+))|(chembl[0-9]+))', re.I), 'chembl.molecule_chembl_id'),
    (re.compile(r'chebi\:[0-9]+', re.I), ['chebi.id', 'chebi.secondary_chebi_id']),
    (re.compile(r'((unii\:(?P<term>[A-Z0-9]{10}))|([A-Z0-9]{10}))', re.I), 'unii.unii'),
    (re.compile(r'((drugbank\:(?P<term>db[0-9]+))|(db[0-9]+))', re.I), ['unichem.drugbank', 'chebi.xrefs.drugbank', 'drugcentral.xrefs.drugbank_id', 'pharmgkb.xrefs.drugbank']),
    (re.compile(r'((pharmgkb.drug\:(?P<term>pa[0-9]+))|(pa[0-9]+))', re.I), 'pharmgkb.id'),
    (re.compile(r'((((pubchem.compound\:)|(cid\:))(?P<term>[0-9]+))|([0-9]+))', re.I), ['pubchem.cid']),
    (re.compile(r'((((sid\:)|(pubchem.substance\:))(?P<term>[0-9]+))|([0-9]+))', re.I), ['fda_orphan_drug.pubchem_sid'])
]

STATUS_CHECK = {
    'id': 'USNINKBPBVKHHZ-CYUUQNCZSA-L',  # penicillin
    'index': 'mychem_current',
}
