import glob
import os

import biothings.hub.dataload.storage as storage
from biothings.hub.datatransform import DataTransformMDB

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .unii_parser import load_data

SRC_META = {
    "url": 'https://precision.fda.gov/uniisearch',
    "license": "public domain",
    "license_url": "https://www.nlm.nih.gov/web_policies.html",
    "license_url_short": "http://bit.ly/2Pg8Oo9"
}


class UniiUploader(BaseDrugUploader):

    name = "unii"
    storage_class = storage.IgnoreDuplicatedStorage
    __metadata__ = {"src_meta": SRC_META}

    keylookup = MyChemKeyLookup([('inchikey', 'unii.inchikey'),
                                 ('smiles', 'unii.smiles'),
                                 ('pubchem', 'unii.pubchem'),
                                 ('unii', 'unii.unii'),
                                 ('drugname', 'unii.preferred_term'),
                                 ('drugcentral', 'unii.drugcentral')],
                                copy_from_doc=True,
                                )

    def load_data(self, data_folder):
        self.logger.info("Load data from '%s'" % data_folder)
        record_files = glob.glob(os.path.join(data_folder, "*Records*.txt"))
        if len(record_files) != 1:
            raise AssertionError(
                "Expecting one record.txt file, got %s" % repr(record_files))
        input_file = record_files.pop()
        if not os.path.exists(input_file):
            raise AssertionError("Can't find input file '%s'" % input_file)
        return self.keylookup(load_data)(input_file)

    def post_update_data(self, *args, **kwargs):
        """create indexes following upload"""
        # Key identifiers for UNII lookups based on the keylookup graph
        index_fields = [
            "unii.unii",                 # Primary UNII identifier
            "unii.preferred_term",       # Drug name lookup
            "unii.inchikey",             # Structural identifier
            "unii.smiles",               # Structural identifier
            "unii.pubchem",              # PubChem cross-reference
            "unii.drugcentral"           # DrugCentral cross-reference
        ]

        for field in index_fields:
            self.logger.info("Indexing '%s'" % field)
            self.collection.create_index(field, background=True)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "unii": {
                "properties": {
                    "unii": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        'copy_to': ['all'],
                    },
                    "display_name": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": ["name"]
                    },
                    "registry_number": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "ec": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "ncit": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "rxcui": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "itis": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "ncbi": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "plants": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "grin": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "inn_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "molecular_formula": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "inchikey": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "smiles": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "ingredient_type": {
                        "type": "text"
                    },
                    "pubchem": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "mpns": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    }
                }
            }
        }

        return mapping
