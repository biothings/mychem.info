import importlib.util
import os
import subprocess
import sys
import textwrap
from pathlib import Path


SOURCE_ROOT = Path(__file__).parents[1]
PARSER_PATH = (
    SOURCE_ROOT / "hub/dataload/sources/drugcentral/drugcentral_parser.py"
)


def load_parser_module():
    spec = importlib.util.spec_from_file_location("drugcentral_parser", PARSER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parser_only_exposes_identifiers_and_stable_source_id(monkeypatch, tmp_path):
    parser = load_parser_module()
    empty = lambda _path: {}
    for processor_name in (
        "process_pharmacology_action",
        "process_faers",
        "process_act",
        "process_omop",
        "process_approval",
        "process_drug_dosage",
        "process_synonym",
    ):
        monkeypatch.setattr(parser, processor_name, empty)

    inchikey = "AAAAAAAAAAAAAA-BBBBBBBBBB-C"
    monkeypatch.setattr(
        parser,
        "process_structure",
        lambda _path: {
            "42": {
                "inchikey": inchikey,
                "inchi": "InChI=1S/example",
                "smiles": "CCO",
                "cas_rn": "64-17-5",
            }
        },
    )
    monkeypatch.setattr(
        parser,
        "process_identifier",
        lambda _path: {
            "42": {
                "unii": ["UNII42"],
                "rxnorm": ["RX42"],
                "drugbank_id": ["DB0042"],
                "chebi": ["CHEBI:42"],
                "chembl_id": ["CHEMBL42"],
                "pubchem_cid": ["42"],
            }
        },
    )

    docs = list(parser.load_data(tmp_path))

    assert len(docs) == 1
    assert docs[0]["_id"] == "DrugCentral:42"
    assert docs[0]["drugcentral"]["id"] == "42"
    assert docs[0]["drugcentral"]["structures"] == {
        "inchikey": inchikey,
        "inchi": "InChI=1S/example",
        "smiles": "CCO",
        "cas_rn": "64-17-5",
    }
    assert docs[0]["drugcentral"]["xrefs"] == {
        "unii": "UNII42",
        "rxnorm": "RX42",
        "drugbank_id": "DB0042",
        "chebi": "CHEBI:42",
        "chembl_id": "CHEMBL42",
        "pubchem_cid": "42",
    }
    assert not hasattr(parser, "xrefs_2_inchikey")
    assert "requests" not in parser.__dict__


HUB_TEST_SETUP = r"""
import importlib
import logging
import os
import sys
import tempfile
import types

config = types.ModuleType("drugcentral_test_config")
config.__file__ = os.path.join(tempfile.gettempdir(), "drugcentral_test_config.py")
config.HUB_DB_BACKEND = {
    "module": "biothings.utils.sqlite3",
    "sqlite_db_folder": tempfile.mkdtemp(prefix="drugcentral-hubdb-"),
}
config.DATA_HUB_DB_DATABASE = "hubdb"
config.DATA_SRC_DATABASE = "srcdb"
config.DATA_SRC_SERVER = "unused"
config.DATA_SRC_PORT = 27017
config.DATA_ARCHIVE_ROOT = tempfile.mkdtemp(prefix="drugcentral-data-")
config.DRUGCENTRAL_PASSWORD = "unused"
config.logger = logging.getLogger("drugcentral-test")
sys.modules[config.__name__] = config
sys.modules["config"] = config
os.environ["HUB_CONFIG"] = config.__name__
"""


def run_hub_test(script):
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(SOURCE_ROOT), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(HUB_TEST_SETUP + script)],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_index_blocks_drugcentral_source_discovery():
    run_hub_test(
        r"""
from biothings.hub.datatransform import datatransform_mdb

class FakeCollection:
    def __init__(self, indexes):
        self.indexes = indexes
        self.database = None
        self.find_calls = 0

    def list_indexes(self):
        return [{"key": {field: 1}} for field in self.indexes]

    def find(self, *args, **kwargs):
        self.find_calls += 1
        raise AssertionError("Source discovery must not perform a lookup")


class FakeDatabase:
    def __init__(self, index_fields):
        self.collections = {
            name: FakeCollection(indexes) for name, indexes in index_fields.items()
        }
        for collection in self.collections.values():
            collection.database = self

    def collection_names(self):
        return list(self.collections)

    def __getitem__(self, name):
        return self.collections[name]


fake_db = FakeDatabase(
    {
        "chembl": {
            "chembl.inchi",
            "chembl.molecule_chembl_id",
            "chembl.chebi_par_id",
            "chembl.smiles",
        },
        "drugbank_full": {
            "drugbank.inchi",
            "drugbank.products.ndc_product_code",
        },
        "pubchem": {"pubchem.inchi", "pubchem.cid"},
        "drugbank": {"drugbank.id", "drugbank.xrefs.chebi"},
        "pharmgkb": {"pharmgkb.id"},
        # chebi.smiles is deliberately absent.
        "chebi": {"chebi.id"},
        "unii": {"unii.unii", "unii.preferred_term", "unii.smiles"},
        "drugcentral": {"drugcentral.structures.smiles"},
    }
)
datatransform_mdb.mongo.get_src_db = lambda: fake_db

try:
    importlib.import_module("hub.dataload.sources.drugcentral")
except ValueError as exc:
    message = str(exc)
else:
    raise AssertionError("DrugCentral discovery ignored a missing lookup index")

assert "chebi.smiles" in message
assert all(collection.find_calls == 0 for collection in fake_db.collections.values())
"""
    )


def test_drugcentral_identifier_resolution_and_index_validation():
    run_hub_test(
        r"""
from biothings.hub.dataload import storage
from biothings.hub.datatransform import datatransform_mdb


def nested_value(doc, path):
    value = doc
    for part in path.split("."):
        value = value[part]
    return value


class FakeCollection:
    def __init__(self, indexes=(), docs=()):
        self.indexes = set(indexes)
        self.docs = list(docs)
        self.database = None
        self.find_calls = 0

    def list_indexes(self):
        return [{"key": {field: 1}} for field in self.indexes]

    def find(self, query, projection):
        self.find_calls += 1
        lookup, condition = next(iter(query.items()))
        lookup_ids = set(condition["$in"])
        matches = []
        for doc in self.docs:
            try:
                value = nested_value(doc, lookup)
            except KeyError:
                continue
            values = value if isinstance(value, list) else [value]
            if lookup_ids.intersection(values):
                matches.append(doc)
        return matches


class FakeDatabase:
    def __init__(self, collections):
        self.collections = collections
        for collection in collections.values():
            collection.database = self

    def collection_names(self):
        return list(self.collections)

    def __getitem__(self, name):
        return self.collections[name]


unii = FakeCollection(
    indexes={"unii.unii", "unii.preferred_term", "unii.smiles"}
)
chebi = FakeCollection(indexes={"chebi.id", "chebi.smiles"})
chembl = FakeCollection(
    indexes={
        "chembl.inchi",
        "chembl.molecule_chembl_id",
        "chembl.chebi_par_id",
        "chembl.smiles",
    }
)
drugcentral = FakeCollection(indexes={"drugcentral.structures.smiles"})
drugbank_full = FakeCollection(
    indexes={"drugbank.inchi", "drugbank.products.ndc_product_code"}
)
pubchem = FakeCollection(indexes={"pubchem.inchi", "pubchem.cid"})
drugbank = FakeCollection(indexes={"drugbank.id", "drugbank.xrefs.chebi"})
pharmgkb = FakeCollection(indexes={"pharmgkb.id"})
fake_db = FakeDatabase(
    {
        "unii": unii,
        "chebi": chebi,
        "chembl": chembl,
        "drugcentral": drugcentral,
        "drugbank_full": drugbank_full,
        "pubchem": pubchem,
        "drugbank": drugbank,
        "pharmgkb": pharmgkb,
    }
)
datatransform_mdb.mongo.get_src_db = lambda: fake_db

from hub.dataload.sources.chebi import ChebiUploader
from hub.dataload.sources.chembl import ChemblUploader
from hub.dataload.sources.drugcentral import DrugCentralUploader
from hub.dataload.sources.unii import UniiUploader

keylookup = DrugCentralUploader.keylookup
assert DrugCentralUploader.storage_class is storage.RootKeyMergerStorage
assert set(keylookup.input_types) == {
    ("inchikey", "drugcentral.structures.inchikey"),
    ("unii", "drugcentral.xrefs.unii"),
    ("rxnorm", "drugcentral.xrefs.rxnorm"),
    ("drugbank", "drugcentral.xrefs.drugbank_id"),
    ("chebi", "drugcentral.xrefs.chebi"),
    ("chembl", "drugcentral.xrefs.chembl_id"),
    ("pubchem", "drugcentral.xrefs.pubchem_cid"),
    ("cas", "drugcentral.structures.cas_rn"),
    ("inchi", "drugcentral.structures.inchi"),
    ("smiles", "drugcentral.structures.smiles"),
}


class IndexRecorder:
    def __init__(self):
        self.fields = []
        self.collection = self
        self.logger = logging.getLogger("index-recorder")

    def create_index(self, index, **kwargs):
        if isinstance(index, list):
            index = index[0][0]
        self.fields.append(index)


for uploader_class, required_field in (
    (ChebiUploader, "chebi.smiles"),
    (ChemblUploader, "chembl.smiles"),
    (DrugCentralUploader, "drugcentral.structures.smiles"),
    (UniiUploader, "unii.smiles"),
):
    recorder = IndexRecorder()
    uploader_class.post_update_data(recorder)
    assert required_field in recorder.fields

direct_key = "AAAAAAAAAAAAAA-BBBBBBBBBB-C"
direct = {
    "_id": "DrugCentral:1",
    "drugcentral": {
        "id": "1",
        "structures": {"inchikey": direct_key},
        "xrefs": {"unii": "UNII-direct"},
    },
}
assert [doc["_id"] for doc in keylookup.lookup_one(direct)] == [direct_key]
assert unii.find_calls == 0

fallback = {
    "_id": "DrugCentral:2",
    "drugcentral": {"id": "2", "xrefs": {"unii": [], "chebi": []}},
}
assert [doc["_id"] for doc in keylookup.lookup_one(fallback)] == [
    "DrugCentral:2"
]

resolved_key = "CCCCCCCCCCCCCC-DDDDDDDDDD-E"
unii.docs = [
    {"unii": {"unii": "UNII3", "inchikey": resolved_key}},
]
resolved = {
    "_id": "DrugCentral:3",
    "drugcentral": {"id": "3", "xrefs": {"unii": "UNII3"}},
}
assert [doc["_id"] for doc in keylookup.lookup_one(resolved)] == [resolved_key]
assert unii.find_calls > 0

invalid_direct = {
    "_id": "DrugCentral:3-invalid",
    "drugcentral": {
        "id": "3-invalid",
        "structures": {"inchikey": "not-an-inchikey"},
        "xrefs": {"unii": "UNII3"},
    },
}
assert [doc["_id"] for doc in keylookup.lookup_one(invalid_direct)] == [
    resolved_key
]

multi_keys = {
    "EEEEEEEEEEEEEE-FFFFFFFFFF-G",
    "GGGGGGGGGGGGGG-HHHHHHHHHH-I",
}
unii.docs = [
    {"unii": {"unii": "UNII4", "inchikey": value}}
    for value in multi_keys
]
multiple = {
    "_id": "DrugCentral:4",
    "drugcentral": {"id": "4", "xrefs": {"unii": "UNII4"}},
}
assert {doc["_id"] for doc in keylookup.lookup_one(multiple)} == multi_keys

smiles_doc = {
    "_id": "DrugCentral:5",
    "drugcentral": {"id": "5", "structures": {"smiles": "CCO"}},
}
smiles_key = "IIIIIIIIIIIIII-JJJJJJJJJJ-K"
second_smiles_key = "KKKKKKKKKKKKKK-LLLLLLLLLL-M"
chebi.docs = [
    {"chebi": {"smiles": "CCO", "inchikey": smiles_key}},
]
chembl.docs = [
    {"chembl": {"smiles": "CCO", "inchi_key": second_smiles_key}},
]
assert {doc["_id"] for doc in keylookup.lookup_one(smiles_doc)} == {
    smiles_key,
    second_smiles_key,
}
assert all(
    collection.find_calls > 0
    for collection in (chebi, chembl, drugcentral, unii)
)
"""
    )
