import os.path
from .cohd_parser import load_data
import biothings.hub.dataload.uploader as uploader

SRC_META = {
    "url": "http://cohd.smart-api.info/",
    "license_url": "",
    "license_url_short": "",
    "license": "CC BY-NC 4.0",
}


class COHDUploader(uploader.BaseSourceUploader):

    name = "cohd"
    __metadata__ = {"src_meta": SRC_META}

    def load_data(self, data_folder):
        cohd_docs = load_data()
        return cohd_docs

    @classmethod
    def get_mapping(klass):
        mapping = {
            "omop": {
                "properties": {
                    "omop": {
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
