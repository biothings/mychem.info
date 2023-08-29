drugbank_mapping = {
    "drugbank": {
        "properties": {
            "FASTA_sequences": {
                "type": "text"
            },
            "accession_number": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "pmids": {
                "type": "integer"
            },
            "carriers": {
                "properties": {
                    "actions": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "general_function": {
                        "type": "text"
                    },
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "known_action": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    },
                    "organism": {
                        "type": "text"
                    },
                    "source": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "specific_function": {
                        "type": "text"
                    },
                    "uniprot": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "pmids": {
                        "type": "integer"
                    },
                    "gene_name": {
                        "type": "text"
                    }
                },
            },
            "categories": {
                "properties": {
                    "category": {
                        "type": "text"
                    },
                    "mesh-id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    }
                }
            },
            "drug_interactions": {
                "properties": {
                    "description": {
                        "type": "text"
                    },
                    "drugbank-id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    }
                }
            },
            "enzymes": {
                "properties": {
                    "actions": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "general_function": {
                        "type": "text"
                    },
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "known_action": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    },
                    "organism": {
                        "type": "text"
                    },
                    "source": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "specific_function": {
                        "type": "text"
                    },
                    "uniprot": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "pmids": {
                        "type": "integer"
                    },
                    "gene_name": {
                        "type": "text"
                    }
                },
            },
            "experimental_properties": {
                "properties": {
                    "boiling_point": {
                        "type": "text"
                    },
                    "caco2_permeability": {
                        "type": "float"
                    },
                    "hydrophobicity": {
                        "type": "float"
                    },
                    "isoelectric_point": {
                        "type": "float"
                    },
                    "logp": {
                        "type": "float"
                    },
                    "logs": {
                        "type": "float"
                    },
                    "melting_point": {
                        "type": "text"
                    },
                    "molecular_formula": {
                        "type": "text"
                    },
                    "molecular_weight": {
                        "type": "float"
                    },
                    "pka": {
                        "type": "text"
                    },
                    "water_solubility": {
                        "type": "text"
                    },
                    "radioactivity": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                }
            },
            "food-interactions": {
                "type": "text"
            },
            "food_interactions": {
                "type": "text"
            },
            "formula": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "groups": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "id": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword",
                "copy_to": ["all"]
            },
            "inchi": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "inchi_key": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "international_brands": {
                "properties": {
                    "company": {
                        "type": "text"
                    },
                    "name": {
                        "type": "text"
                    }
                }
            },
            "iupac": {
                "type": "text"
            },
            "manufacturers": {
                "type": "text"
            },
            "mixtures": {
                "properties": {
                    "ingredients": {
                        "type": "text"
                    },
                    "name": {
                        "type": "text"
                    }
                }
            },
            "name": {
                "type": "text",
                "copy_to": ["all"]
            },
            "packagers": {
                "type": "text"
            },
            "patents": {
                "properties": {
                    "country": {
                        "type": "text"
                    },
                    "expires": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "number": {
                        "type": "text"
                    },
                    "pediatric-extension": {
                        "type": "boolean"
                    }
                }
            },
            "pathways": {
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "smpdb_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    }
                }
            },
            "reactions": {
                "properties": {
                    "product": {
                        "properties": {
                            "drugbank_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "name": {
                                "type": "text"
                            }
                        }
                    },
                    "enzymes": {
                        "properties": {
                            "drugbank_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "name": {
                                "type": "text"
                            },
                            "uniprot-id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    }
                }
            },
            "pharmacology": {
                "properties": {
                    "absorption": {
                        "type": "text"
                    },
                    "affected_organisms": {
                        "type": "text"
                    },
                    "clearance": {
                        "type": "text"
                    },
                    "description": {
                        "type": "text"
                    },
                    "half_life": {
                        "type": "text"
                    },
                    "indication": {
                        "type": "text"
                    },
                    "mechanism_of_action": {
                        "type": "text"
                    },
                    "metabolism": {
                        "type": "text"
                    },
                    "pharmacodynamics": {
                        "type": "text"
                    },
                    "protein_binding": {
                        "type": "text"
                    },
                    "route_of_elimination": {
                        "type": "text"
                    },
                    "snp_adverse_drug_reactions": {
                        "properties": {
                            "reaction": {
                                "properties": {
                                    "adverse-reaction": {
                                        "type": "text"
                                    },
                                    "allele": {
                                        "type": "text"
                                    },
                                    "description": {
                                        "type": "text"
                                    },
                                    "gene-symbol": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "protein-name": {
                                        "type": "text"
                                    },
                                    "pubmed-id": {
                                        "type": "integer"
                                    },
                                    "rs-id": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "uniprot-id": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            }
                        }
                    },
                    "snp_effects": {
                        "properties": {
                            "effect": {
                                "properties": {
                                    "allele": {
                                        "type": "text"
                                    },
                                    "defining-change": {
                                        "type": "text"
                                    },
                                    "description": {
                                        "type": "text"
                                    },
                                    "gene-symbol": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "protein-name": {
                                        "type": "text"
                                    },
                                    "pubmed-id": {
                                        "type": "integer"
                                    },
                                    "rs-id": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "uniprot-id": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            }
                        }
                    },
                    "toxicity": {
                        "type": "text"
                    },
                    "volume_of_distribution": {
                        "type": "text"
                    }
                }
            },
            "predicted_properties": {
                "properties": {
                    "bioavailability": {
                        "type": "boolean"
                    },
                    "ghose_filter": {
                        "type": "boolean"
                    },
                    "h_bond_acceptor_count": {
                        "type": "integer"
                    },
                    "h_bond_donor_count": {
                        "type": "integer"
                    },
                    "logp": {
                        "type": "float"
                    },
                    "logs": {
                        "type": "float"
                    },
                    "mddr_like_rule": {
                        "type": "boolean"
                    },
                    "number_of_rings": {
                        "type": "integer"
                    },
                    "physiological_charge": {
                        "type": "integer"
                    },
                    "pka_(strongest_acidic)": {
                        "type": "float"
                    },
                    "pka_(strongest_basic)": {
                        "type": "float"
                    },
                    "polar_surface_area_(psa)": {
                        "type": "float"
                    },
                    "polarizability": {
                        "type": "float"
                    },
                    "refractivity": {
                        "type": "float"
                    },
                    "rotatable_bond_count": {
                        "type": "integer"
                    },
                    "rule_of_five": {
                        "type": "boolean"
                    },
                    "water_solubility": {
                        "type": "text"
                    }
                }
            },
            "products": {
                "properties": {
                    "approved": {
                        "type": "boolean"
                    },
                    "country": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "dosage_form": {
                        "type": "text"
                    },
                    "dpd": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "ended_marketing_on": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "fda_application_number": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "generic": {
                        "type": "boolean"
                    },
                    "name": {
                        "type": "text"
                    },
                    "ndc_product_code": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "otc": {
                        "type": "boolean"
                    },
                    "route": {
                        "type": "text"
                    },
                    "source": {
                        "type": "text"
                    },
                    "started_marketing_on": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "strength": {
                        "type": "text"
                    }
                }
            },
            "salts": {
                "properties": {
                    "name": {
                        "type": "text",
                    },
                    "unii": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "cas-number": {
                        "type": "text"
                    },
                    "inchikey": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "average-mass": {
                        "type": "float"
                    },
                    "monoisotopic-mass": {
                        "type": "float"
                    }
                }
            },
            "smiles": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "synonyms": {
                "type": "text"
            },
            "targets": {
                "properties": {
                    "actions": {
                        "type": "text"
                    },
                    "general_function": {
                        "type": "text"
                    },
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "known_action": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    },
                    "organism": {
                        "type": "text"
                    },
                    "source": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "specific_function": {
                        "type": "text"
                    },
                    "uniprot": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "pmids": {
                        "type": "integer"
                    },
                    "gene_name": {
                        "type": "text"
                    }
                }
            },
            "taxonomy": {
                "properties": {
                    "alternative-parent": {
                        "type": "text"
                    },
                    "class": {
                        "type": "text"
                    },
                    "description": {
                        "type": "text"
                    },
                    "direct-parent": {
                        "type": "text"
                    },
                    "kingdom": {
                        "type": "text"
                    },
                    "subclass": {
                        "type": "text"
                    },
                    "substituent": {
                        "type": "text"
                    },
                    "superclass": {
                        "type": "text"
                    }
                }
            },
            "traditional_iupac_name": {
                "type": "text"
            },
            "transporters": {
                "properties": {
                    "actions": {
                        "type": "text"
                    },
                    "general_function": {
                        "type": "text"
                    },
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "known_action": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    },
                    "organism": {
                        "type": "text"
                    },
                    "source": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "specific_function": {
                        "type": "text"
                    },
                    "uniprot": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "pmids": {
                        "type": "integer"
                    },
                    "gene_name": {
                        "type": "text"
                    }
                }
            },
            "weight": {
                "properties": {
                    "average": {
                        "type": "float"
                    },
                    "monoisotopic": {
                        "type": "float"
                    }
                }
            },
            "xrefs": {
                "properties": {
                    "ahfs_codes": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "atc_codes": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "bindingdb": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "chebi": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "chembl": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "chemspider": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "dpd": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "drugs_com": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "genbank": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "guide_to_pharmacology": {
                        "type": "integer"
                    },
                    "iuphar": {
                        "type": "integer"
                    },
                    "kegg": {
                        "properties": {
                            "cid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "did": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "pdb": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "pdrhealth": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "pharmgkb": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "pubchem": {
                        "properties": {
                            "cid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "sid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "rxlist": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "therapeutic_targets_database": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "uniprotkb": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "wikipedia": {
                        "properties": {
                            "url_stub": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    }
                }
            }
        }
    }
}
