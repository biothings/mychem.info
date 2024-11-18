"""
Chembl uploader
"""
import glob

# pylint: disable=E0401, E0611
import os

import biothings.hub.dataload.storage as storage
from biothings.hub.dataload.uploader import ParallelizedSourceUploader

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .chembl_parser import AuxiliaryDataLoader, MoleculeDataLoader, load_chembl_data

SRC_META = {
    "url": 'https://www.ebi.ac.uk/chembl/',
    "license_url": "https://www.ebi.ac.uk/about/terms-of-use",
    "license_url_short": "http://bit.ly/2KAUCAm"
}


class ChemblUploader(BaseDrugUploader, ParallelizedSourceUploader):
    """
    ChemblUploader - upload the Chembl data source
    """

    name = "chembl"
    storage_class = storage.RootKeyMergerStorage
    __metadata__ = {"src_meta": SRC_META}

    MOLECULE_FILENAME_PATTERN = "molecule.*.json"
    DRUG_INDICATION_FILENAME_PATTERN = "drug_indication.*.json"
    MECHANISM_FILENAME_PATTERN = "mechanism.*.json"
    TARGET_FILENAME_PATTERN = "target.*.json"
    BINDING_SITE_FILENAME_PATTERN = "binding_site.*.json"

    keylookup = MyChemKeyLookup(
        [
            ("inchikey", "chembl.inchi_key"),
            ("inchi", "chembl.inchi"),
            ("chembl", "chembl.molecule_chembl_id"),
            ("chebi", "chembl.chebi_par_id"),
            ("drugcentral", "chembl.xrefs.drugcentral.id"),
            ("smiles", "chembl.smiles"),
            ("pubchem", "chembl.xrefs.pubchem.cid"),
        ],
        # TODO:  handle duplicate keys from pubchem
        # we use RootKeyMergerStorage, but the num. duplicates is too high (>10000)
        # ("pubchem", "chembl.xrefs.pubchem.sid"),
        copy_from_doc=True)

    def jobs(self):
        """
        this method will be called by self.update_data() and then generate arguments for self.load.data() method,
        allowing parallelization
        """
        molecule_filepaths = glob.glob(os.path.join(
            self.data_folder, self.MOLECULE_FILENAME_PATTERN))
        mol_data_loaders = [MoleculeDataLoader(
            molecule_filepath=filepath) for filepath in molecule_filepaths]

        drug_indication_filepaths = glob.iglob(os.path.join(
            self.data_folder, self.DRUG_INDICATION_FILENAME_PATTERN))
        mechanism_filepaths = glob.iglob(os.path.join(
            self.data_folder, self.MECHANISM_FILENAME_PATTERN))
        target_filepaths = glob.iglob(os.path.join(
            self.data_folder, self.TARGET_FILENAME_PATTERN))
        binding_site_filepaths = glob.iglob(os.path.join(
            self.data_folder, self.BINDING_SITE_FILENAME_PATTERN))
        aux_data_loader = AuxiliaryDataLoader(drug_indication_filepaths=drug_indication_filepaths,
                                              mechanism_filepaths=mechanism_filepaths,
                                              target_filepaths=target_filepaths,
                                              binding_site_filepaths=binding_site_filepaths)
        aux_data_loader.eagerly_load()

        return [(mol_data_loader, aux_data_loader) for mol_data_loader in mol_data_loaders]

    def load_data(self, mol_data_loader: MoleculeDataLoader, aux_data_loader: AuxiliaryDataLoader):
        """load data from an input file"""
        self.logger.info("Load data from file '%s'" %
                         mol_data_loader.molecule_filepath)

        return self.keylookup(load_chembl_data, debug=True)(mol_data_loader, aux_data_loader)

    def post_update_data(self, *args, **kwargs):
        """create indexes following an update"""
        # pylint: disable=W0613
        """
        for idxname in ["chembl.chebi_par_id", "chembl.inchi", "chembl.molecule_chembl_id"]:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true or it'll lock the whole database...
            self.collection.create_index(idxname, background=True)
        """
        for idxname in ["chembl.chebi_par_id", "chembl.molecule_chembl_id", "chembl.inchi"]:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true, or it'll lock the whole database...
            self.collection.create_index(idxname, background=True)

    @classmethod
    def get_mapping(cls):
        """return mapping data"""
        mapping = {
            "chembl": {
                "properties": {
                    "drug_indications": {
                        "properties": {
                            "efo": {
                                "properties": {
                                    "id": {
                                        "type": "keyword"
                                    },
                                    "term": {
                                        "type": "text"
                                    }
                                }
                            },
                            "first_approval": {
                                "type": "integer"
                            },
                            "indication_refs": {
                                "properties": {
                                    "id": {
                                        "type": "keyword"
                                    },
                                    "type": {
                                        "type": "keyword"
                                    },
                                    "url": {
                                        "type": "text"
                                    },
                                    "ClinicalTrials": {
                                        "type": "text"
                                    },
                                    "ATC": {
                                        "type": "text"
                                    },
                                    "DailyMed": {
                                        "type": "text"
                                    },
                                    "FDA": {
                                        "type": "text"
                                    }
                                }
                            },
                            "max_phase_for_ind": {
                                "type": "keyword"
                            },
                            "mesh_heading": {
                                "type": "text"
                            },
                            "mesh_id": {
                                "type": "keyword"
                            }
                        }
                    },
                    "drug_mechanisms": {
                        "properties": {
                            "action_type": {
                                "type": "keyword"
                            },
                            "binding_site_name": {
                                "type": "text"
                            },
                            "mechanism_refs": {
                                "properties": {
                                    "id": {
                                        "type": "keyword"
                                    },
                                    "type": {
                                        "type": "keyword"
                                    },
                                    "url": {
                                        "type": "text"
                                    },
                                    "ISBN": {
                                        "type": "text"
                                    },
                                    "PubMed": {
                                        "type": "text"
                                    },
                                    "DailyMed": {
                                        "type": "text"
                                    },
                                    "Wikipedia": {
                                        "type": "text"
                                    },
                                    "Expert": {
                                        "type": "text"
                                    },
                                    "Other": {
                                        "type": "text"
                                    },
                                    "FDA": {
                                        "type": "text"
                                    },
                                    "DOI": {
                                        "type": "text"
                                    },
                                    "KEGG": {
                                        "type": "text"
                                    },
                                    "PubChem": {
                                        "type": "text"
                                    },
                                    "IUPHAR": {
                                        "type": "text"
                                    },
                                    "PMC": {
                                        "type": "text"
                                    },
                                    "InterPro": {
                                        "type": "text"
                                    },
                                    "ClinicalTrials": {
                                        "type": "text"
                                    },
                                    "Patent": {
                                        "type": "text"
                                    },
                                    "UniProt": {
                                        "type": "text"
                                    }
                                }
                            },
                            "target_chembl_id": {
                                "type": "keyword"
                            },
                            "target_components": {
                                "properties": {
                                    "uniprot": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "ensembl_gene": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            },
                            "target_name": {
                                "type": "text"
                            },
                            "target_organism": {
                                "type": "text"
                            },
                            "target_type": {
                                "type": "text"
                            }
                        }
                    },
                    "biotherapeutic": {
                        "properties": {
                            "helm_notation": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "description": {
                                "type": "text"
                            },
                            "biocomponents": {
                                "properties": {
                                    "organism": {
                                        "type": "text"
                                    },
                                    "tax_id": {
                                        "type": "integer"
                                    },
                                    "sequence": {
                                        "type": "text"
                                    },
                                    "component_id": {
                                        "type": "integer"
                                    },
                                    "description": {
                                        "type": "text"
                                    },
                                    "component_type": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            },
                            "molecule_chembl_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                "copy_to": [
                                    "all"
                                ]
                            }
                        }
                    },
                    "therapeutic_flag": {
                        "type": "boolean"
                    },
                    "usan_stem": {
                        "type": "text"
                    },
                    "molecule_chembl_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "molecule_properties": {
                        "properties": {
                            "heavy_atoms": {
                                "type": "integer"
                            },
                            "acd_most_bpka": {
                                "type": "float"
                            },
                            "mw_freebase": {
                                "type": "float"
                            },
                            "num_ro5_violations": {
                                "type": "integer"
                            },
                            "molecular_species": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "qed_weighted": {
                                "type": "float"
                            },
                            "ro3_pass": {
                                "type": "boolean"
                            },
                            "full_mwt": {
                                "type": "float"
                            },
                            "num_lipinski_ro5_violations": {
                                "type": "integer"
                            },
                            "rtb": {
                                "type": "integer"
                            },
                            "psa": {
                                "type": "float"
                            },
                            "alogp": {
                                "type": "float"
                            },
                            "hbd": {
                                "type": "integer"
                            },
                            "acd_most_apka": {
                                "type": "float"
                            },
                            "hbd_lipinski": {
                                "type": "integer"
                            },
                            "acd_logp": {
                                "type": "float"
                            },
                            "full_molformula": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "aromatic_rings": {
                                "type": "integer"
                            },
                            "hba_lipinski": {
                                "type": "integer"
                            },
                            "mw_monoisotopic": {
                                "type": "float"
                            },
                            "hba": {
                                "type": "integer"
                            },
                            "acd_logd": {
                                "type": "float"
                            }
                        }
                    },
                    "helm_notation": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "max_phase": {
                        "type": "keyword"
                    },
                    "inorganic_flag": {
                        "type": "integer"
                    },
                    "usan_stem_definition": {
                        "type": "text"
                    },
                    "dosed_ingredient": {
                        "type": "boolean"
                    },
                    "chebi_par_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "withdrawn_reason": {
                        "type": "text"
                    },
                    "molecule_hierarchy": {
                        "properties": {
                            "parent_chembl_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "molecule_chembl_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "prodrug": {
                        "type": "integer"
                    },
                    "withdrawn_flag": {
                        "type": "boolean"
                    },
                    "usan_year": {
                        "type": "integer"
                    },
                    "parenteral": {
                        "type": "boolean"
                    },
                    "black_box_warning": {
                        "type": "integer"
                    },
                    "polymer_flag": {
                        "type": "boolean"
                    },
                    "molecule_synonyms": {
                        "properties": {
                            "molecule_synonym": {
                                "type": "text"
                            },
                            "synonyms": {
                                "type": "text"
                            },
                            "syn_type": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "atc_classifications": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "molecule_type": {
                        "type": "text"
                    },
                    "first_in_class": {
                        "type": "integer"
                    },
                    "inchi": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "structure_type": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "withdrawn_class": {
                        "type": "text"
                    },
                    "inchi_key": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "topical": {
                        "type": "boolean"
                    },
                    "oral": {
                        "type": "boolean"
                    },
                    "xrefs": {
                        "properties": {
                            "drugcentral": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "tg-gates": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "wikipedia": {
                                "properties": {
                                    "url_stub": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            },
                            "dailymed": {
                                "properties": {
                                    "name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "pubchem": {
                                "properties": {
                                    "sid": {
                                        "type": "integer"
                                    }
                                }
                            }
                        }
                    },
                    "chirality": {
                        "type": "integer"
                    },
                    "usan_substem": {
                        "type": "text"
                    },
                    "indication_class": {
                        "type": "text"
                    },
                    "withdrawn_country": {
                        "type": "text"
                    },
                    "withdrawn_year": {
                        "type": "integer"
                    },
                    "availability_type": {
                        "type": "integer"
                    },
                    "smiles": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "natural_product": {
                        "type": "integer"
                    },
                    "pref_name": {
                        "type": "text",
                        "copy_to": [
                            "all",
                            "name"
                        ]
                    },
                    "first_approval": {
                        "type": "integer"
                    }
                }
            }
        }

        return mapping
