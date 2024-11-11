import os

import biothings.hub.dataload.storage as storage
import pymongo
from biothings.utils.exclude_ids import ExcludeFieldsById
from biothings.utils.mongo import get_src_db

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .chebi_parser import ChebiParser, CompoundReader, OntologyReader
from .exclusion_ids import exclusion_ids

SRC_META = {
    "url": 'https://www.ebi.ac.uk/chebi/',
    "license_url": "https://www.ebi.ac.uk/about/terms-of-use",
    "license_url_short": "http://bit.ly/2KAUCAm"
}


class ChebiUploader(BaseDrugUploader):

    name = "chebi"
    # storage_class = storage.IgnoreDuplicatedStorage
    storage_class = storage.RootKeyMergerStorage
    __metadata__ = {"src_meta": SRC_META}
    keylookup = MyChemKeyLookup([('inchikey', 'chebi.inchikey'),
                                 ('drugbank', 'chebi.xrefs.drugbank'),
                                 ('chebi', 'chebi.id'),
                                 ('smiles', 'chebi.smiles')],
                                copy_from_doc=True)

    """
    A document with an ID from `exclusion_ids` would have a long list for one or more of the following fields:

    - `chebi.xrefs.intenz`
    - `chebi.xrefs.rhea`
    - `chebi.xrefs.uniprot`
    - `chebi.xrefs.sabio_rk`
    - `chebi.xrefs.patent`

    `ExcludeFieldsById` acts like a filter to truncate the length of such long lists to 1,000.

    See the comment on the ExcludeFieldsById for use of this class.
    """
    exclude_fields = ExcludeFieldsById(exclusion_ids, [
        "chebi.xrefs.intenz",
        "chebi.xrefs.rhea",
        "chebi.xrefs.uniprot",
        "chebi.xrefs.sabio_rk",
        "chebi.xrefs.patent",
    ])

    def load_data(self, data_folder):
        self.logger.info("Load data from '%s'" % data_folder)

        sdf_input_file = os.path.join(data_folder, "ChEBI_complete.sdf")
        assert os.path.exists(
            sdf_input_file), "Can't find input file '%s'" % sdf_input_file

        obo_input_file = os.path.join(data_folder, "chebi_lite.obo")
        assert os.path.exists(
            obo_input_file), "Can't find input file '%s'" % obo_input_file

        # get others source collection for inchi key conversion
        drugbank_col = get_src_db()["drugbank"]
        assert drugbank_col.count() > 0, \
            "'drugbank' collection is empty (required for inchikey conversion). Please run 'drugbank' uploader first"
        chembl_col = get_src_db()["chembl"]
        assert chembl_col.count() > 0, \
            "'chembl' collection is empty (required for inchikey conversion). Please run 'chembl' uploader first"

        compound_reader = CompoundReader(sdf_input_file)
        ontology_reader = OntologyReader(obo_input_file)
        chebi_parser = ChebiParser(compound_reader, ontology_reader)

        # KeyLookup is disabled due to duplicate key errors
        return self.exclude_fields(self.keylookup(chebi_parser.parse, debug=True))()
        # return self.exclude_fields(load_data)(input_file)

    def post_update_data(self, *args, **kwargs):
        for idxname in ["chebi.id"]:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true or it'll lock the whole database...
            self.collection.create_index(
                [(idxname, pymongo.ASCENDING)], background=True)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "chebi": {
                "properties": {
                    "brand_names": {
                        "type": "text",
                        'copy_to': ['all'],
                    },
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        'copy_to': ['all'],
                    },
                    "iupac": {
                        "type": "text"
                    },
                    "inchi": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "definition": {
                        "type": "text"
                    },
                    "star": {
                        "type": "integer"
                    },
                    "smiles": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "last_modified": {
                        "type": "text"
                    },
                    "inn": {
                        "type": "text"
                    },
                    "xrefs": {
                        "properties": {
                            "molbase": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "resid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "come": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "pubchem": {
                                "properties": {
                                    "sid": {
                                        "type": "integer"
                                    },
                                    "cid": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "beilstein": {
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
                            "metacyc": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "biomodels": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "reactome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "um_bbd_compid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "lincs": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "uniprot": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "sabio_rk": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "patent": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "pdbechem": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "arrayexpress": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "cas": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "lipid_maps_class": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "kegg_drug": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "knapsack": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "lipid_maps_instance": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "intenz": {
                                "type": "text"
                            },
                            "kegg_glycan": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "ecmdb": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "hmdb": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "kegg_compound": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "ymdb": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "drugbank": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "rhea": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "gmelin": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "intact": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            }
                        }
                    },
                    "monoisotopic_mass": {
                        "type": "float"
                    },
                    "mass": {
                        "type": "float"
                    },
                    "secondary_chebi_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        'copy_to': ['all'],
                    },
                    "formulae": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "inchikey": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "name": {
                        "type": "text",
                        'copy_to': ['all', 'name'],
                    },
                    "charge": {
                        "type": "integer"
                    },
                    "synonyms": {
                        "type": "text"
                    },
                    "citation": {
                        "properties": {
                            "pubmed": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "agricola": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "pmc": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "chinese_abstracts": {
                                "type": "integer"
                            },
                            "citexplore": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            }
                        }
                    },
                    "num_children": {
                        "type": "integer"
                    },
                    "children": {
                        "type": "text"
                    },
                    "num_parents": {
                        "type": "integer"
                    },
                    "parents": {
                        "type": "text"
                    },
                    "num_descendants": {
                        "type": "integer"
                    },
                    "descendants": {
                        "type": "text"
                    },
                    "num_ancestors": {
                        "type": "integer"
                    },
                    "ancestors": {
                        "type": "text"
                    },
                    "relationship": {
                        "properties": {
                            "has_functional_parent": {
                                "type": "text"
                            },
                            "has_parent_hydride": {
                                "type": "text"
                            },
                            "has_part": {
                                "type": "text"
                            },
                            "has_role": {
                                "type": "text"
                            },
                            "is_conjugate_acid_of": {
                                "type": "text"
                            },
                            "is_conjugate_base_of": {
                                "type": "text"
                            },
                            "is_enantiomer_of": {
                                "type": "text"
                            },
                            "is_substituent_group_from": {
                                "type": "text"
                            },
                            "is_tautomer_of": {
                                "type": "text"
                            }
                        }
                    }
                }
            }
        }
        return mapping
