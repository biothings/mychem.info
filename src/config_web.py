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
    (re.compile(r'db[0-9]+', re.I), 'drugbank.id'),
    (re.compile(r'chembl[0-9]+', re.I), 'chembl.molecule_chembl_id'),
    (re.compile(r'chebi\:[0-9]+', re.I), ['chebi.id', 'chebi.secondary_chebi_id']),
    (re.compile(r'[A-Z0-9]{10}'), 'unii.unii'),
    (re.compile(r'((cid\:(?P<term>[0-9]+))|([0-9]+))', re.I), 'pubchem.cid')
]

STATUS_CHECK = {
    'id': 'USNINKBPBVKHHZ-CYUUQNCZSA-L',  # penicillin
    'index': 'mychem_current',
}
