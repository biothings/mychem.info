import glob
import os.path

from hub.datatransform.keylookup import MyChemKeyLookup

# when code is exported, import becomes relative
try:
    from pubchem.pubchem_parser import load_annotations as parser_func
except ImportError:
    from .pubchem_parser import load_annotations as parser_func


# from parser import load_data
import biothings.hub.dataload.storage as storage

# from hub.dataload.uploader import BaseDrugUploader
from biothings.hub.dataload.uploader import ParallelizedSourceUploader


class PubChemUploader(ParallelizedSourceUploader):

    name = "pubchem"
    storage_class = storage.RootKeyMergerStorage

    __metadata__ = {
        "src_meta": {
            "url": "https://pubchem.ncbi.nlm.nih.gov/",
            "license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
            "license_url_short": "http://bit.ly/2AqoLOc",
            "license": "public domain"
        }
    }

    COMPOUND_PATTERN = "Compound*.xml.gz"

    keylookup = MyChemKeyLookup(
        [
            ('inchikey', 'pubchem.inchikey'),
            ('inchi', 'pubchem.inchi'),
            ('smiles', 'pubchem.smiles.canonical'),
            ('pubchem', 'pubchem.cid')
        ],
        copy_from_doc=True,
    )

    def jobs(self):
        # this will generate arguments for self.load.data() method, allowing parallelization
        xmlgz_files = glob.glob(os.path.join(
            self.data_folder, self.__class__.COMPOUND_PATTERN))
        return [(f,) for f in xmlgz_files]

    def load_data(self, input_file):
        self.logger.info("Load data from file '%s'" % input_file)
        return self.keylookup(parser_func)(input_file)

    def post_update_data(self, *args, **kwargs):
        """create indexes following upload"""
        for idxname in ["pubchem.cid", "pubchem.inchi"]:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true or it'll lock the whole database...
            # pubchem can be an array, hence it doesn't support hashed indexes
            self.collection.create_index(idxname, background=True)

    @classmethod
    def get_mapping(klass):
        return {
            "pubchem": {
                "properties": {
                    "cid": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        'copy_to': ['all'],
                    },
                    "iupac": {
                        "properties": {
                            "allowed": {
                                "type": "text"
                            },
                            "cas_like_style": {
                                "type": "text"
                            },
                            "markup": {
                                "type": "text"
                            },
                            "preferred": {
                                "type": "text"
                            },
                            "systematic": {
                                "type": "text"
                            },
                            "traditional": {
                                "type": "text"
                            }
                        }
                    },
                    "smiles": {
                        "properties": {
                            "canonical": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "isomeric": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "formal_charge": {
                        "type": "integer"
                    },
                    "complexity": {
                        "type": "float"
                    },
                    "hydrogen_bond_acceptor_count": {
                        "type": "integer"
                    },
                    "hydrogen_bond_donor_count": {
                        "type": "integer"
                    },
                    "rotatable_bond_count": {
                        "type": "integer"
                    },
                    "inchi": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "inchikey": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "xlogp": {
                        "type": "float"
                    },
                    "exact_mass": {
                        "type": "float"
                    },
                    "molecular_formula": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "molecular_weight": {
                        "type": "float"
                    },
                    "topological_polar_surface_area": {
                        "type": "float"
                    },
                    "monoisotopic_weight": {
                        "type": "float"
                    },
                    "heavy_atom_count": {
                        "type": "integer"
                    },
                    "chiral_atom_count": {
                        "type": "integer"
                    },
                    "chiral_bond_count": {
                        "type": "integer"
                    },
                    "defined_chiral_atom_count": {
                        "type": "integer"
                    },
                    "undefined_chiral_atom_count": {
                        "type": "integer"
                    },
                    "defined_chiral_bond_count": {
                        "type": "integer"
                    },
                    "undefined_chiral_bond_count": {
                        "type": "integer"
                    },
                    "isotope_atom_count": {
                        "type": "integer"
                    },
                    "covalent_unit_count": {
                        "type": "integer"
                    },
                    "tautomers_count": {
                        "type": "integer"
                    }
                }
            }
        }
