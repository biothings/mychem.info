def get_customized_mapping(cls):
    mapping = {
        "gtopdb": {
            "properties": {
                "name": {"type": "text"},
                "type": {"type": "text"},
                "ligand_id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "approved": {"type": "boolean"},
                "inn": {"type": "text"},
                "synonyms": {"type": "text"},
                "smiles": {"type": "keyword"},
                "inchikey": {"type": "keyword"},
                "inchi": {"type": "keyword"},
                "no_of_interaction_targets": {"type": "integer"},
                "interaction_targets": {
                    "properties": {
                        "target_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "entrez_gene": {"type": "text"},
                        "ensembl_gene": {"type": "text"},
                        "symbol": {"type": "text"},
                        "target_ligand_id": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "species": {"type": "text"},
                        "target_ligand": {"type": "text"},
                        "name": {"type": "text"},
                    }
                },
                "xrefs": {
                    "properties": {
                        "cas": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "pubchem_cid": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "pubchem_sid": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "uniprotkb": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                        "ensembl": {
                            "normalizer": "keyword_lowercase_normalizer",
                            "type": "keyword",
                        },
                    }
                },
                "clinical_use_comment": {"type": "text"},
                "iupac_name": {"type": "text"},
                "gtoimmupdb": {"type": "boolean"},
                "labelled": {"type": "boolean"},
                "radioactive": {"type": "boolean"},
                "species": {"type": "text"},
                "bioactivity_comment": {"type": "text"},
                "antibacterial": {"type": "boolean"},
                "gtompdb": {"type": "boolean"},
                "withdrawn": {"type": "boolean"},
                "ligand_subunit_ids": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "ligand_subunit_name": {"type": "text"},
                "ligand_subunit_uniprot_ids": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
                "ligand_subunit_ensembl_ids": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                },
            }
        }
    }
    return mapping
