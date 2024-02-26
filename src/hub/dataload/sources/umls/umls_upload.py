from .umls_parser import load_data
import biothings.hub.dataload.uploader as uploader


SRC_META = {
        "url": 'https://www.nlm.nih.gov/research/umls/index.html',
        "license_url": "https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/license_agreement.html"
        }

class UMLSUploader(uploader.BaseSourceUploader):

    name = "umls"

    def load_data(self, data_folder):
        umls_docs = load_data(data_folder)
        return umls_docs

    @classmethod
    def get_mapping(klass):
        mapping = {
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
                        "copy_to": ["all"]
                    }
                }
            }
        }
        return mapping
