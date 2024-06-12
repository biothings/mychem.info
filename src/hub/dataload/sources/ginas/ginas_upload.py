import biothings.hub.dataload.uploader as uploader


class GinasUploader(uploader.DummySourceUploader):

    name = "ginas"
    __metadata__ = {
        "src_meta": {
            "url": "https://ginas.ncats.nih.gov",
            "license_url": "?",
        }
    }

    @classmethod
    def get_mapping(klass):
        mapping = {
            "ginas": {
                "properties": {
                    "cas_primary": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "relationships": {
                        "properties": {
                            "type": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            }
                        }
                    },
                    "unii": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "approvalID": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "definitionLevel": {
                        "type": "text",
                    },
                    "inchikey": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "mixture_unii": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "mixture_inchikey": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "names_list": {
                        "type": "text"
                    },
                    "preferred_name": {
                        "type": "text",
                        "copy_to": ["all", "name"]
                    },
                    "properties": {
                        "type": "text",
                    },
                    "status": {
                        "type": "text"
                    },
                    "substanceClass": {
                        "type": "text"
                    },
                    "tags": {
                        "type": "text",
                    },
                    "uuid": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "xrefs": {
                        "properties": {
                            "CAS": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "DRUG BANK": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "MESH": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "NCI_THESAURUS": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "RXCUI": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "WIKIPEDIA": {
                                "type": "text",
                            }
                        }
                    },
                }
            }
        }

        return mapping
