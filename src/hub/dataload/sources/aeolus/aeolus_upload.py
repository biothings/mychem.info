# import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader

# from biothings.utils.mongo import get_src_conn

# from hub.datatransform.keylookup import MyChemKeyLookup


class AeolusUploader(uploader.DummySourceUploader):
    name = "aeolus"
    __metadata__ = {
        "src_meta": {
            "url": "http://www.nature.com/articles/sdata201626",
            "license_url": "http://datadryad.org/resource/doi:10.5061/dryad.8q0s4",
            "license_url_short": "http://bit.ly/2DIxWwF",
            "license": "CC0 1.0"
        }
    }

    # storage_class = storage.RootKeyMergerStorage
    # keylookup = MyChemKeyLookup(
    #     [('inchikey', 'aeolus.inchikey'),
    #      ('unii', 'aeolus.unii'),
    #      ('drugname', 'aeolus.drug_name')],
    #     copy_from_doc=True
    # )

    # def load_data(self, data_folder):
    #     # read data from the source collection
    #     src_col = self.db[self.src_col_name]

    #     def load_data():
    #         yield from src_col.find()

    #     # perform keylookup on source collection
    #     return self.keylookup(load_data, debug=True)()

    @classmethod
    def get_mapping(klass):
        mapping = {
            "aeolus": {
                "properties": {
                    "indications": {
                        "properties": {
                            "id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "meddra_code": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "count": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "text"
                            }
                        }
                    },
                    "no_of_outcomes": {
                        "type": "integer"
                    },
                    "inchikey": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "rxcui": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "outcomes": {
                        "properties": {
                            "id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "meddra_code": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "name": {
                                "type": "text"
                            },
                            "prr_95_ci": {
                                "type": "float"
                            },
                            "ror": {
                                "type": "float"
                            },
                            "ror_95_ci": {
                                "type": "float"
                            },
                            "case_count": {
                                "type": "long"
                            },
                            "prr": {
                                "type": "float"
                            }
                        }
                    },
                    "drug_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "unii": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "drug_name": {
                        "type": "text",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "pt": {
                        "type": "text"
                    }
                }
            }
        }
        return mapping
