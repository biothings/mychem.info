import os.path

import biothings.hub.dataload.uploader as uploader

from hub.datatransform.keylookup import MyChemKeyLookup

from .cohd_parser import load_data

SRC_META = {
    "url": "http://cohd.smart-api.info/",
    "license_url": "",
    "license_url_short": "",
    "license": "CC BY-NC 4.0",
}


class COHDUploader(uploader.BaseSourceUploader):

    name = "cohd"
    __metadata__ = {"src_meta": SRC_META}

    keylookup = MyChemKeyLookup(
        [("omop", "omop.omop"),
         ("drugname", "omop.name")],
        copy_from_doc=True)

    def load_data(self, data_folder):
        cohd_docs = self.keylookup(load_data)()
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
