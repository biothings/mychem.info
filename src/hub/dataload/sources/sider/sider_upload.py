"""
Sider Uploader
"""
# pylint: disable=E0401, E0611
import os
from biothings.hub.datatransform import IDStruct
from biothings.hub.datatransform import nested_lookup
from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup
from .sider_parser import load_data
from .sider_parser import sort_key


SRC_META = {
    "url": 'http://sideeffects.embl.de/',
    "license_url" : "ftp://xi.embl.de/SIDER/LICENSE",
    "license_url_short" : "http://bit.ly/2SjPTpx",
    "license": "CC BY-NC-SA 3.0"
    }


def preproc(doc):
    """preprocess a sider id"""
    _id = doc["_id"]
    assert _id.startswith('CID')
    assert len(_id) == 12
    return doc


class SiderIDStruct(IDStruct):
    """Custom IDStruct to preprocess _id from sider"""

    def preprocess_id(self,_id):
        if isinstance(_id, str) and _id.startswith('CID') and len(_id) == 12:
            return int(_id[4:])
        return _id

    def _init_strct(self, field, doc_lst):
        """
        initialze _id_tuple_lst

        In this class, stitch identifiers are converted to pubchem identifiers
        for keylookup.  This is done internally by this class which performs a
        preprocessing conversion to an identifier.
        """
        for doc in doc_lst:
            value = nested_lookup(doc, field)
            if value:
                self.add(value, self.preprocess_id(value))

    @property
    def id_lst(self):
        id_set = set()
        for key in self.forward:
            for val in self.forward[key]:
                id_set.add(self.preprocess_id(val))
        return list(id_set)

    def find_right(self, ids):
        """Find the first id founding by searching the (_, right) identifiers"""
        inverse = {}
        for rid in self.inverse:
            inverse[self.preprocess_id(rid)] = self.inverse[rid]
        return self.find(inverse, ids)


class SiderUploader(BaseDrugUploader):
    """
    SiderUploader - Biothings Sider Uploader class
    """

    name = "sider"
    #storage_class = storage.IgnoreDuplicatedStorage
    __metadata__ = {"src_meta" : SRC_META}
    keylookup = MyChemKeyLookup(
        [("pubchem", "_id")],
        idstruct_class=SiderIDStruct)
    max_lst_size = 2000

    def load_data(self, data_folder):
        """load_data method"""
        input_file = os.path.join(data_folder, "merged_freq_all_se_indications.tsv")
        self.logger.info("Load data from file '%s'" % input_file)
        docs = self.keylookup(load_data)(input_file)
        for doc in docs:
            # sort the 'sider' list by "sider.side_effect.frequency" and "sider.side_effect.name"
            # pylint: disable=W0108
            doc['sider'] = sorted(doc['sider'],
                                  key=lambda x: sort_key(x))
            # take at most self.max_lst_size elements from the 'sider' field
            # See the 'truncated_docs.tsv' file for a list of ids that are affected
            if len(doc['sider']) > self.max_lst_size:
                doc['sider'] = doc['sider'][:self.max_lst_size]

            yield doc

    @classmethod
    def get_mapping(cls):
        """get mapping data for sider"""
        mapping = {
            "sider": {
                "properties": {
                    "stitch": {
                        "properties": {
                            "flat": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                },
                            "stereo": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                }
                            }
                        },
                    "indication": {
                        "properties": {
                            "method_of_detection": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                },
                            "name": {
                                "type": "text"
                                }
                            }
                        },
                    "meddra": {
                        "properties": {
                            "type": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                },
                            "umls_id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                }
                            }
                        },
                    "side_effect": {
                        "properties": {
                            "frequency": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                },
                            "placebo": {
                                "type": "boolean"
                                },
                            "name": {
                                "type": "text"
                                }
                            }
                        }
                    }
                }
        }
        return mapping
