import biothings.hub.dataload.uploader as uploader

from hub.datatransform.keylookup import MyChemKeyLookup

from .umls_parser import load_data

SRC_META = {
    "url": 'https://www.nlm.nih.gov/research/umls/index.html',
    "license_url": "https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html"
}


class UMLSUploader(uploader.BaseSourceUploader):

    name = "umls"

    keylookup = MyChemKeyLookup(
        [
    ('mesh', 'umls.mesh'),
    ('umls', 'umls.cui')
    ]

    def load_data(self, data_folder):
        return self.keylookup(load_data)(input_file)
        return umls_docs

    @ classmethod
    def get_mapping(klass):
        mapping={
            "umls": {
                "properties": {
                    "cui": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                        'copy_to': ['all'],
                    },
                    "mesh": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                        'copy_to': ['all'],
                    },
                    "name": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                        "copy_to": ["all", "name"]
                    }
                }
            }
        }
        return mapping
