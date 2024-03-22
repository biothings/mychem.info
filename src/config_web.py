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
    "compound": "mychem_current",
}
ES_SCROLL_TIME = "10m"

# *****************************************************************************
# Endpoint Specifics
# *****************************************************************************

# *** NOTE ***
# The CHEBI prefix must have a regex_term_pattern without a named <term> grouping.
# example query: CHEBI:57966:
# code snippet location: <biothings.api/web/query/builder.py>
# With a named term grouping of <term>, we produce the following which will fail
#     named_groups = match.groupdict() -> {"term": 57966}
#     q = named_groups.get(self.gpname.term) or q -> "57966"
# Without a named term grouping of <term> we orduce the following which will pass
#     named_groups = match.groupdict() -> {}
#     q = named_groups.get(self.gpname.term) or q -> "CHEBI:57966"

BIOLINK_MODEL_PREFIX_BIOTHINGS_CHEM_MAPPING = {
    "INCHIKEY": {"type": "chem"},
    "CHEMBL.COMPOUND": {
        "type": "chem",
        "field": "chembl.molecule_chembl_id",
        "regex_term_pattern": "(?P<term>chembl[0-9]+)",
        # "converter": lambda x: x.replace("CHEMBL.COMPOUND:", "CHEMBL"),
    },
    "PUBCHEM.COMPOUND": {
        "type": "chem",
        "field": "pubchem.cid",
        "regex_term_pattern": "(?P<term>[0-9]+)",
    },
    "CHEBI": {
        "type": "chem",
        "field": ["chebi.id", "chebi.secondary_chebi_id"],
        "regex_term_pattern": "(?P<term>CHEBI:[0-9]+)",
    },
    "UNII": {
        "type": "chem",
        "field": "unii.unii",
        "regex_term_pattern": "(?P<term>[A-Z0-9]{10})",
    },
}

# CURIE ID support based on BioLink Model
biolink_curie_regex_list = []
for (
    biolink_prefix,
    mapping,
) in BIOLINK_MODEL_PREFIX_BIOTHINGS_CHEM_MAPPING.items():
    field_match = mapping.get("field", [])
    term_pattern = mapping.get("regex_term_pattern", None)
    if term_pattern is None:
        term_pattern = "(?P<term>[^:]+)"

    raw_expression = rf"({biolink_prefix}):{term_pattern}"
    compiled_expression = re.compile(raw_expression, re.I)

    pattern = (compiled_expression, field_match)
    biolink_curie_regex_list.append(pattern)

# Custom prefix handling for chem specific identifiers
chem_prefix_handling = [
    (
        re.compile(r"((chembl\:(?P<term>chembl[0-9]+))|(chembl[0-9]+))", re.I),
        "chembl.molecule_chembl_id",
    ),
    (re.compile(r"chebi\:[0-9]+", re.I), ["chebi.id", "chebi.secondary_chebi_id"]),
    (re.compile(r"((unii\:(?P<term>[A-Z0-9]{10}))|([A-Z0-9]{10}))", re.I), "unii.unii"),
    (
        re.compile(r"((drugbank\:(?P<term>db[0-9]+))|(db[0-9]+))", re.I),
        [
            "unichem.drugbank",
            "chebi.xrefs.drugbank",
            "drugcentral.xrefs.drugbank_id",
            "pharmgkb.xrefs.drugbank",
        ],
    ),
    (
        re.compile(r"((pharmgkb.drug\:(?P<term>pa[0-9]+))|(pa[0-9]+))", re.I),
        "pharmgkb.id",
    ),
    (
        re.compile(
            r"((((pubchem.compound\:)|(cid\:))(?P<term>[0-9]+))|([0-9]+))", re.I
        ),
        ["pubchem.cid"],
    ),
    (
        re.compile(
            r"((((sid\:)|(pubchem.substance\:))(?P<term>[0-9]+))|([0-9]+))", re.I
        ),
        ["fda_orphan_drug.pubchem_sid"],
    ),
]

default_chem_regex = re.compile(r"(?P<scope>[^:]+):(?P<term>[\W\w]+)")
default_chem_fields = ()
default_chem_regex_pattern = (default_chem_regex, default_chem_fields)


ANNOTATION_ID_REGEX_LIST = [
    *biolink_curie_regex_list,
    *chem_prefix_handling,
    default_chem_regex_pattern,
]


STATUS_CHECK = {
    "id": "USNINKBPBVKHHZ-CYUUQNCZSA-L",  # penicillin
    "index": "mychem_current",
}

_extra_kwargs = {"list_filter": {"type": str, "default": None}}
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS["*"].update(_extra_kwargs)
QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS["*"].update(_extra_kwargs)
ES_RESULT_TRANSFORM = "web.pipeline.MyChemESResultFormatter"
