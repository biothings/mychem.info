"""
DrugBank Uploader
"""
import glob

# pylint: disable=E0401, E0611
import os

import biothings.hub.dataload.storage as storage
import pymongo
from biothings.utils.common import unzipall
from biothings.utils.exclude_ids import ExcludeFieldsById

from hub.dataload.uploader import BaseDrugUploader
from hub.datatransform.keylookup import MyChemKeyLookup

from .drugbank_open_mapping import drugbank_open_mapping
from .drugbank_open_parser import load_data
from .exclusion_ids import exclusion_ids

SRC_META = {
    "url": "http://www.drugbank.ca",
    "license_url": "https://go.drugbank.com/releases/latest#open-data",
    "license_url_short": "https://bit.ly/3Hikpvm",
    "license": "CC0",
}


class DrugBankOpenUploader(BaseDrugUploader):
    """
    DrugBankUploader - biothings uploader class for DrugBank
    """

    name = "drugbank"
    storage_class = storage.IgnoreDuplicatedStorage
    __metadata__ = {"src_meta": SRC_META}
    # See the comment on the ExcludeFieldsById for use of this class.
    exclude_fields = ExcludeFieldsById(exclusion_ids, [
        "drugbank.drug_interactions",
        "drugbank.products",
        "drugbank.mixtures"
    ])
    keylookup = MyChemKeyLookup(
        [("inchikey", "drugbank.inchi_key"),
         ("unii", "drugbank.unii"),
         ("drugbank", "drugbank.id"),
         ("chebi", "drugbank.xrefs.chebi"),
         ("chembl", "drugbank.xrefs.chembl"),
         ("pubchem", "drugbank.xrefs.pubchem.cid"),
         ("inchi", "drugbank.inchi"),
         ("drugname", "drugbank.name"),
         ],
        copy_from_doc=True)

    def load_data(self, data_folder):
        """load_data from data source"""
        csvfiles = glob.glob(os.path.join(data_folder, "*.csv"))
        if not csvfiles:
            self.logger.info("Unzipping drugbank open vocabulary")
            unzipall(data_folder)
            self.logger.info("Load data from '%s'" % data_folder)
            csvfiles = glob.glob(os.path.join(data_folder, "*.csv"))
        if len(csvfiles) != 1:
            raise ValueError("Expecting one csv file, got %s" % repr(csvfiles))
        input_file = csvfiles.pop()
        if not os.path.exists(input_file):
            raise FileNotFoundError("Can't find input file '%s'" % input_file)
        return self.exclude_fields(self.keylookup(load_data, debug=True))(input_file)

    def post_update_data(self, *args, **kwargs):
        """create indexes following upload"""
        # Add/Remove indexes based on your CSV structure.
        for idxname in ["drugbank.id", "drugbank.inchi_key"]:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true or it'll lock the whole database...
            self.collection.create_index(
                [(idxname, pymongo.HASHED)], background=True)

    @classmethod
    def get_mapping(cls):
        """return mapping information for drugbank"""
        return drugbank_open_mapping
