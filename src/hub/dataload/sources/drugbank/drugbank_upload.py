"""
DrugBank Uploader
"""
import os

# pylint: disable=E0401, E0611

import pymongo
import biothings.hub.dataload.storage as storage
from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .drugbank_mapping import drugbank_mapping
from .drugbank_parser import load_data


SRC_META = {
    "url": "http://go.drugbank.com",
    "license_url": "https://go.drugbank.com/releases/latest#open-data",
    "license": "CC0",
}


class DrugBankUploader(BaseDrugUploader):
    """
    DrugBankUploader - biothings uploader class for DrugBank
    """

    name = "drugbank"
    # Merge documents with the same _id
    storage_class = storage.RootKeyMergerStorage
    __metadata__ = {"src_meta": SRC_META}

    keylookup = MyChemKeyLookup([
         ("inchikey", "drugbank.inchikey"),
         ("drugbank", "drugbank.id"),
         ("unii", "drugbank.unii"),
         ("drugname", "drugbank.name")
    ], copy_from_doc=True)

    def load_data(self, data_folder):
        """load_data from data source"""
        csvfile = os.path.join(data_folder, "drugbank vocabulary.csv")
        assert os.path.exists(csvfile), f"Can't find input file: {csvfile}"
        return self.keylookup(load_data, debug=True)(csvfile)

    def post_update_data(self, *args, **kwargs):
        # pylint: disable=W0613
        """create indexes following upload"""
        for idxname in [
            "drugbank.id",
            "drugbank.unii"
        ]:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true or it'll lock the whole database...
            self.collection.create_index([(idxname, pymongo.HASHED)],
                                         background=True)

    @classmethod
    def get_mapping(cls):
        """return mapping information for drugbank"""
        return drugbank_mapping
