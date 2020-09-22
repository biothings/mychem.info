import os.path
from .cohd_parser import load_data
import biothings.hub.dataload.uploader as uploader


class COHDUploader(uploader.BaseSourceUploader):

    name = "cohd"

    def load_data(self, data_folder):
        cohd_docs = load_data()
        return cohd_docs

    @classmethod
    def get_mapping(klass):
        mapping = {
            "cohd": {
                "properties": {
                    "cohd": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer",
                        'copy_to': ['all'],
                    },
                    "name": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    }
                }
            }
        }
        return mapping
