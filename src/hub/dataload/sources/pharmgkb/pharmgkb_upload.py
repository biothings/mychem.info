"""
PharmGKB Biothings Uploader
"""
# pylint: disable=E0401, E0611
import os

import biothings.hub.dataload.storage as storage

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .pharmgkb_parser import load_data

SRC_META = {
    "url": 'https://www.pharmgkb.org/',
    "license_url": "https://www.pharmgkb.org/page/dataUsagePolicy",
    "license_url_short": "http://bit.ly/2zqM8aJ",
    "license": "CC BY-SA 4.0"
}


class PharmGkbUploader(BaseDrugUploader):
    """
    PharmGKB Uploader Class
    """

    name = "pharmgkb"
    storage_class = storage.RootKeyMergerStorage
    __metadata__ = {"src_meta": SRC_META}
    keylookup = MyChemKeyLookup(
        [
            ('inchi', 'pharmgkb.inchi'),
            ('drugbank', 'pharmgkb.xrefs.drugbank'),
            ('chebi', 'pharmgkb.xrefs.chebi'),
            ('mesh', 'pharmgkb.xrefs.mesh'),
            ('umls', 'pharmgkb.xrefs.umls'),
            ('smiles', 'pharmgkb.smiles'),
            ('cas', 'pharmgkb.xrefs.cas'),
            ('ndc', 'pharmgkb.xrefs.ndc'),
            ('pubchem', 'pharmgkb.xrefs.pubchem.cid'),
            ('pubchem', 'pharmgkb.xrefs.pubchem.sid'),
            ('rxnorm', 'pharmgkb.xrefs.rxnorm'),
            ('pharmgkb', 'unichem.pharmgkb')

        ])

    def load_data(self, data_folder):
        """load_data method"""
        self.logger.info("Load data from '%s'" % data_folder)
        input_file = os.path.join(data_folder, "drugs.tsv")
        assert os.path.exists(
            input_file), "Can't find input file '%s'" % input_file
        return self.keylookup(load_data)(input_file)

    def post_update_data(self, *args, **kwargs):
        field = "pharmgkb.id"
        self.logger.info("Indexing '%s'" % field)
        self.collection.create_index(field, background=True)

    @classmethod
    def get_mapping(cls):
        """get mapping information"""
        mapping = {
            "pharmgkb": {
                "properties": {
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        'copy_to': ['all'],
                    },
                    "dosing_guideline": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "inchi": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "name": {
                        "type": "text",
                        'copy_to': ['all', 'name'],
                    },
                    "smiles": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "generic_names": {
                        "type": "text",
                        'copy_to': ['all'],
                    },
                    'brand_mixtures': {
                        'properties': {
                            'brand_name': {
                                'type': 'text'
                            },
                            'mixture': {
                                'type': 'text'
                            }
                        }
                    },
                    "trade_names": {
                        "type": "text"
                    },
                    "type": {
                        "type": "text"
                    },
                    "xrefs": {
                        "properties": {
                            "web_resource": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "uniprotkb": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "pubchem": {
                                "properties": {
                                    "sid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    },
                                    "cid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    }
                                }
                            },
                            "het": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "wikipedia": {
                                "properties": {
                                    "url_stub": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    }
                                }
                            },
                            "iuphar_ligand": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "meddra": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "atc": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "kegg_compound": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "umls": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "clinicaltrials": {
                                "properties": {
                                    "gov": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    }
                                }
                            },
                            "genbank": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "rxnorm": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "chebi": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "cas": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "ttd": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "kegg_drug": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "mesh": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "ndc": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "chemspider": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "hmdb": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "dailymed": {
                                "properties": {
                                    "setid": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword",
                                    }
                                }
                            },
                            "ndfrt": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "bindingdb": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "drugbank": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "pdb": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "dpd": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            }
                        }
                    }
                }
            }
        }
        return mapping
