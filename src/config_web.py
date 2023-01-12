"""
    Mychem.info
    https://mychem.info/
    Chemical and Drug Annotation as a Service.
"""
import copy
import re

from biothings.web.settings.default import ANNOTATION_KWARGS, QUERY_KWARGS

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
    (re.compile(r'chembl[0-9]+', re.I), 'chembl.molecule_chembl_id'),
    (re.compile(r'chebi\:[0-9]+', re.I), ['chebi.id', 'chebi.secondary_chebi_id']),
    (re.compile(r'[A-Z0-9]{10}'), 'unii.unii'),
    (re.compile(r'db[0-9]+', re.I), ['unichem.drugbank', 'chebi.xrefs.drugbank', 'drugcentral.xrefs.drugbank_id', 'pharmgkb.xrefs.drugbank']),
    (re.compile(r'pa[0-9]+', re.I), 'pharmgkb.id'),
    (re.compile(r'((cid\:(?P<term>[0-9]+))|([0-9]+))', re.I), ['pubchem.cid', 'fda_orphan_drug.pubchem_sid'])
]

STATUS_CHECK = {
    'id': 'USNINKBPBVKHHZ-CYUUQNCZSA-L',  # penicillin
    'index': 'mychem_current',
}

_extra_kwargs = {
    "list_filter": {"type": str, "default": None}
}
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS["*"].update(_extra_kwargs)
QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS["*"].update(_extra_kwargs)
ES_RESULT_TRANSFORM = "web.pipeline.MyChemESResultFormatter"
