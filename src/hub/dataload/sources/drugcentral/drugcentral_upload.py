import biothings.hub.dataload.storage as storage

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .drugcentral_parser import load_data


class DrugCentralUploader(BaseDrugUploader):

    name = "drugcentral"
    # Using root merger storage because some documents may map to the same _id.
    storage_class = storage.RootKeyMergerStorage

    __metadata__ = {
        "src_meta": {
            "url": "http://drugcentral.org/",
            "license_url": "http://drugcentral.org/privacy",
            "license_url_short": "http://bit.ly/2SeEhUy",
            "license": "CC BY-SA 4.0",
        }
    }

    # Keylookup is a callable object
    keylookup = MyChemKeyLookup(
        [('inchikey', 'drugcentral.structures.inchikey'),
         ('unii', 'drugcentral.xref.unii'),
         # other keys are present but not currently used by keylookup
         ('inchi', 'drugcentral.structures.inchi'),
         ('drugbank', 'drugcentral.xrefs.drugbank_id'),
         ('chebi', 'drugcentral.xrefs.chebi'),
         ('chembl', 'drugcentral.xrefs.chembl_id'),
         ('pubchem', 'drugcentral.xrefs.pubchem_cid'),
         ('smiles', 'drugcentral.structures.smiles'),
         ('mesh', 'drugcentral.xrefs.mesh_supplemental_record_ui'),
         ('umls', 'drugcentral.xrefs.umlscui'),
         ('drugcentral', 'unichem.drugcentral')
         ],
        # ('drugname', 'drugcentral.synonyms')], # unhashable type - list
        copy_from_doc=True,
    )

    def load_data(self, data_folder):
        drugcentral_docs = self.keylookup(load_data, debug=True)(data_folder)
        return drugcentral_docs

    @classmethod
    def get_mapping(klass):
        mapping = {
            "drugcentral": {
                "properties": {
                    "pharmacology_class": {
                        "properties": {
                            "mesh_pa": {
                                "properties": {
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "fda_moa": {
                                "properties": {
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "fda_epc": {
                                "properties": {
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "chebi": {
                                "properties": {
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "fda_cs": {
                                "properties": {
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "fda_pe": {
                                "properties": {
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "fda_ext": {
                                "properties": {
                                    "description": {
                                        "type": "text"
                                    },
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            },
                            "fda_chemical/ingredient": {
                                "properties": {
                                    "code": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            }
                        }
                    },
                    "fda_adverse_event": {
                        "properties": {
                            "meddra_code": {
                                "type": "integer"
                            },
                            "level": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "llr": {
                                "type": "float"
                            },
                            "llr_threshold": {
                                "type": "float"
                            },
                            "drug_ae": {
                                "type": "integer"
                            },
                            "drug_no_ae": {
                                "type": "integer"
                            },
                            "no_drug_ae": {
                                "type": "integer"
                            },
                            "no_drug_no_ar": {
                                "type": "integer"
                            },
                            "meddra_term": {
                                "type": "text"
                            }
                        }
                    },
                    "drug_use": {
                        "properties": {
                            "indication": {
                                "properties": {
                                    "umls_cui": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "cui_semantic_type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "snomed_concept_id": {
                                        "type": "long"
                                    },
                                    "concept_name": {
                                        "type": "text"
                                    },
                                    "snomed_full_name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "contraindication": {
                                "properties": {
                                    "umls_cui": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "cui_semantic_type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "snomed_concept_id": {
                                        "type": "long"
                                    },
                                    "concept_name": {
                                        "type": "text"
                                    },
                                    "snomed_full_name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "off_label_use": {
                                "properties": {
                                    "umls_cui": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "cui_semantic_type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "snomed_concept_id": {
                                        "type": "long"
                                    },
                                    "concept_name": {
                                        "type": "text"
                                    },
                                    "snomed_full_name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "symptomatic_treatment": {
                                "properties": {
                                    "umls_cui": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "concept_name": {
                                        "type": "text"
                                    },
                                    "snomed_full_name": {
                                        "type": "text"
                                    },
                                    "cui_semantic_type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "snomed_concept_id": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "reduce_risk": {
                                "properties": {
                                    "umls_cui": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "concept_name": {
                                        "type": "text"
                                    },
                                    "snomed_full_name": {
                                        "type": "text"
                                    },
                                    "cui_semantic_type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "snomed_concept_id": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "diagnosis": {
                                "properties": {
                                    "umls_cui": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "concept_name": {
                                        "type": "text"
                                    },
                                    "snomed_full_name": {
                                        "type": "text"
                                    },
                                    "cui_semantic_type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "snomed_concept_id": {
                                        "type": "long"
                                    }
                                }
                            }
                        }
                    },
                    "drug_dosage": {
                        "properties": {
                            "dosage": {
                                "type": "float"
                            },
                            "unit": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "route": {
                                "type": "text"
                            }
                        }
                    },
                    "structures": {
                        "properties": {
                            "cas_rn": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "inchi": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "inchikey": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "smiles": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "inn": {
                                "type": "text",
                                "copy_to": [
                                    "all"
                                ]
                            }
                        }
                    },
                    "xrefs": {
                        "properties": {
                            "kegg_drug": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "secondary_cas_rn": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "umlscui": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "chebi": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "chembl_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "mesh_supplemental_record_ui": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "pubchem_cid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "inn_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "unii": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "drugbank_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "rxnorm": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "nddf": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "snomedct_us": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "vandf": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "mmsl": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "nui": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "mesh_descriptor_ui": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "pdb_chem_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "vuid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "iuphar_ligand_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "approval": {
                        "properties": {
                            "date": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "agency": {
                                "type": "text"
                            },
                            "orphan": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "company": {
                                "type": "text"
                            }
                        }
                    },
                    "bioactivity": {
                        "properties": {
                            "uniprot": {
                                "properties": {
                                    "uniprot_id": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "gene_symbol": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "swissprot_entry": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            },
                            "moa": {
                                "type": "float"
                            },
                            "act_value": {
                                "type": "float"
                            },
                            "act_type": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "moa_source": {
                                "type": "text"
                            },
                            "action_type": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "act_source": {
                                "type": "text"
                            },
                            "target_class": {
                                "type": "text"
                            },
                            "target_name": {
                                "type": "text"
                            },
                            "organism": {
                                "type": "text"
                            }
                        }
                    },
                    "synonyms": {
                        "type": "text"
                    }
                }
            }
        }

        return mapping
