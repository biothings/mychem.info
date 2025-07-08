import biothings
import biothings.hub.dataload.uploader

import config
from hub.datatransform.keylookup import MyChemKeyLookup

biothings.config_for_app(config)

# when code is exported, import becomes relative
try:
    from UniChem_BioThings_SDK.parser import load_annotations as parser_func
except ImportError:
    from .parser import load_annotations as parser_func


class Unichem_biothings_sdkUploader(
        biothings.hub.dataload.uploader.BaseSourceUploader):

    name = "unichem"

    __metadata__ = {"src_meta": {
        "url": 'https://www.ebi.ac.uk/unichem',
        "license_url": ("https://s100.copyright.com/AppDispatchServlet?title=UniChem"
                        "%3A%20a%20unified%20chemical%20structure%20cross-referencing"
                        "%20and%20identifier%20tracking%20system&author=Jon%20Chambers"
                        "%20et%20al&contentID=10.1186%2F1758-2946-5-3&publication=1758"
                        "-2946&publicationDate=2013-01-14&publisherName=SpringerNature"
                        "&orderBeanReset=true&oa=CC%20BY"),
        "license_url_short": "https://bit.ly/2CCluAB",
        "license": "CC BY-SA 4.0"
    }
    }

    # idconverter = None
    storage_class = biothings.hub.dataload.storage.BasicStorage

    keylookup = MyChemKeyLookup(
        [("chebi", "unichem.chebi"),
         ("pubchem", "unichem.pubchem"),
         ("chembl", "unichem.chembl"),
         ("rxnorm", "unichem.rxnorm"),
         ("pharmgkb", "unichem.pharmgkb"),
         ("drugbank", "unichem.drugbank"),
         ("drugcentral", "unichem.drugcentral")],
        copy_from_doc=True)

    def load_data(self, data_folder):
        self.logger.info("Load data from directory: '%s'" % data_folder)
        return self.keylookup(parser_func)(data_folder)

    def post_update_data(self, *args, **kwargs):
        """create indexes following upload"""
        # Key identifiers for UniChem lookups based on the keylookup graph
        index_fields = [
            "unichem.chebi",       # Primary target for chemical entity lookups
            "unichem.pubchem",     # PubChem CID identifier
            "unichem.chembl",      # ChEMBL molecule identifier
            "unichem.drugbank",    # DrugBank identifier
            "unichem.pharmgkb",    # PharmGKB identifier
            "unichem.rxnorm",      # RxNorm identifier
            "unichem.drugcentral"  # DrugCentral identifier
        ]

        for idxname in index_fields:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true or it'll lock the whole database...
            # unichem fields can be arrays, hence no hashed indexes
            self.collection.create_index(idxname, background=True)

    @classmethod
    def get_mapping(klass):
        return {
            'unichem': {
                'properties': {
                    'actor': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'atlas': {
                        'type': 'text'
                    },
                    'bindingdb': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'brenda': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'carotenoiddb': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'chebi': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'chembl': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'chemicalbook': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'clinicaltrials': {
                        'type': 'text'
                    },
                    'comptox': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'dailymed': {
                        'type': 'text'
                    },
                    'drugbank': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'drugcentral': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'emolecules': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'fdasrs': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'gtopdb': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'hmdb': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'ibm': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'kegg_ligand': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'lincs': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'lipidmaps': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'mcule': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'metabolights': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'molport': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'nih_ncc': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'nikkaji': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'nmrshiftdb2': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'pdb': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'pharmgkb': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'pubchem': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'pubchem_dotf': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'pubchem_tpharma': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'recon': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'rhea': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'rxnorm': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'selleck': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'surechembl': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'swisslipids': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    },
                    'zinc': {
                        'normalizer': 'keyword_lowercase_normalizer',
                        'type': 'keyword'
                    }
                }
            }
        }
