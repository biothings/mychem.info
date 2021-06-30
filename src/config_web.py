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
    None: "mychem_current",
    "chem": "mychem_current",
    "drug": "mychem_current",
    "compound": "mychem_current"
}
ES_SCROLL_TIME = '10m'

# *****************************************************************************
# App URL Patterns
# *****************************************************************************

GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'drug_get'
GA_ACTION_ANNOTATION_POST = 'drug_post'
GA_TRACKER_URL = 'c.biothings.io'

# *****************************************************************************
# Endpoint Specifics
# *****************************************************************************

ANNOTATION_ID_REGEX_LIST = [
    (re.compile(r'db[0-9]+', re.I), 'drugbank.id'),
    (re.compile(r'chembl[0-9]+', re.I), 'chembl.molecule_chembl_id'),
    (re.compile(r'chebi\:[0-9]+', re.I), ['chebi.id', 'chebi.secondary_chebi_id']),
    (re.compile(r'[A-Z0-9]{10}'), 'unii.unii'),
    (re.compile(r'((cid\:(?P<search_term>[0-9]+))|([0-9]+))', re.I), 'pubchem.cid')
]

STATUS_CHECK = {
    'id': 'USNINKBPBVKHHZ-CYUUQNCZSA-L',  # penicillin
    'index': 'mychem_current',
}
