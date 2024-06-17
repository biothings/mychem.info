"""
NDC Uploader
"""
# pylint: disable=E0401, E0611
import biothings.hub.dataload.storage as storage
from biothings.utils.exclude_ids import ExcludeFieldsById

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .exclusion_ids import exclusion_ids
from .ndc_parser import load_data

SRC_META = {
    "url": "http://www.fda.gov/Drugs/InformationOnDrugs/ucm142438.htm",
    "license_url":
        "https://www.fda.gov/AboutFDA/AboutThisWebsite/WebsitePolicies/default.htm#linking",
    "lincese_url_short": "http://bit.ly/2KAojBn",
    "license": "public domain"
}


class NDCUploader(BaseDrugUploader):
    """
    NDCUploader - Biothings Uploader class for NDC
    """
    name = "ndc"
    storage_class = (storage.RootKeyMergerStorage, storage.CheckSizeStorage)
    __metadata__ = {"src_meta": SRC_META}
    keylookup = MyChemKeyLookup(
        [("ndc", "ndc.productndc"),
         ("drugname", "ndc.nonproprietaryname")])
    # See the comment on the ExcludeFieldsById for use of this class.
    exclude_fields = ExcludeFieldsById(exclusion_ids, ["ndc"])

    def load_data(self, data_folder):
        """load data from the data source"""
        return self.exclude_fields(self.keylookup(load_data))(data_folder)

    @classmethod
    def get_mapping(cls):
        """return mapping data for the class"""
        mapping = {
            "ndc": {
                "properties": {
                    "product_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "productndc": {
                        "type": "text"
                    },
                    "producttypename": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "proprietaryname": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": ["name"]
                    },
                    "proprietarynamesuffix": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "nonproprietaryname": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": ["name"]
                    },
                    "dosageformname": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "routename": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "startmarketingdate": {
                        "type": "text"
                    },
                    "endmarketingdate": {
                        "type": "text"
                    },
                    "marketingcategoryname": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "applicationnumber": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "labelername": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "substancename": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": ["all"]
                    },
                    "active_numerator_strength": {
                        "type": "text"
                    },
                    "active_ingred_unit": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "pharm_classes": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "deaschedule": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                    },
                    "package": {
                        "properties": {
                            "packagedescription": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                            },
                            "ndcpackagecode": {
                                "type": "text"
                            }
                        }
                    }
                }
            }
        }

        return mapping
