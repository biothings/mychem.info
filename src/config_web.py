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
ES_HOST = "localhost:9200"
ES_INDICES = {
    "chem": "mychem_current",
    "drug": "mychem_current",
    "compound": "mychem_current",
}
ES_SCROLL_TIME = "10m"

# *****************************************************************************
# Endpoint Specifics
# *****************************************************************************

BIOLINK_MODEL_PREFIX_BIOTHINGS_CHEM_MAPPING = {
    "INCHIKEY": {"type": "chem"},
    "CHEMBL.COMPOUND": {
        "type": "chem",
        "field": "chembl.molecule_chembl_id",
        # "converter": lambda x: x.replace("CHEMBL.COMPOUND:", "CHEMBL"),
    },
    "PUBCHEM.COMPOUND": {"type": "chem", "field": "pubchem.cid"},
    "CHEBI": {"type": "chem", "field": "chebi.id", "keep_prefix": True},
    "UNII": {"type": "chem", "field": "unii.unii"},
}


# CURIE ID support based on BioLink Model
biolink_curie_regex_list = []
for (
    biolink_prefix,
    mapping,
) in BIOLINK_MODEL_PREFIX_BIOTHINGS_CHEM_MAPPING.items():
    expression = re.compile(rf"({biolink_prefix}):(?P<term>[^:]+)", re.I)
    field_match = mapping.get("field", [])
    pattern = (expression, field_match)
    biolink_curie_regex_list.append(pattern)

# Custom prefix handling for chem specific identifiers
custom_chem_prefix_handling = [
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

# The default pattern is neither the fallback pattern or the biolink
# CURIE ID prefixes match the pattern. This pattern matches the default
# presented in the ESQueryBuilder in the biothings.api library.
# Infers based off empty scopes
default_pattern = (re.compile(r"(?P<scope>[\W\w]+):(?P<term>[^:]+)"), [])

ANNOTATION_ID_REGEX_LIST = [
    *biolink_curie_regex_list,
    *custom_chem_prefix_handling,
    default_pattern,
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
