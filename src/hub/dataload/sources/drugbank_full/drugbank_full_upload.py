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

from .drugbank_full_mapping import drugbank_full_mapping
from .drugbank_full_parser import load_data
from .exclusion_full_ids import exclusion_ids

SRC_META = {
    "url": "http://www.drugbank.ca",
    "license_url": "https://www.drugbank.ca/releases/latest",
    "license_url_short": "http://bit.ly/2PSfZTD",
    "license": "CC BY-NC 4.0",
}


class DrugBankFullUploader(BaseDrugUploader):
    """
    DrugBankUploader - biothings uploader class for DrugBank
    """

    name = "drugbank_full"
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
         ("inchi", "drugbank.inchi"),
         ("smiles", "drugbank.smiles"),
         ("drugbank", "drugbank.id"),
         ("chebi", "drugbank.xrefs.chebi"),
         ("chembl", "drugbank.xrefs.chembl"),
         ("pubchem", "drugbank.xrefs.pubchem.cid"),
         ("unii", "drugbank.unii"),
         ("cas", "drugbank.cas_number"),
         ("drugname", "drugbank.name"),
         ("ndc", "drugbank.products.ndc_product_code")],
        copy_from_doc=True)

    def load_data(self, data_folder):
        """load_data from data source"""
        xmlfiles = glob.glob(os.path.join(data_folder, "*.xml"))
        if not xmlfiles:
            self.logger.info("Unzipping drugbank archive")
            unzipall(data_folder)
            self.logger.info("Load data from '%s'" % data_folder)
            xmlfiles = glob.glob(os.path.join(data_folder, "*.xml"))
        if len(xmlfiles) != 1:
            raise ValueError("Expecting one xml file, got %s" % repr(xmlfiles))
        input_file = xmlfiles.pop()
        if not os.path.exists(input_file):
            raise FileNotFoundError("Can't find input file '%s'" % input_file)
        return self.exclude_fields(self.keylookup(load_data, debug=True))(input_file)

    def post_update_data(self, *args, **kwargs):
        # pylint: disable=W0613
        """create indexes following upload"""
        # Key identifiers for drugbank lookups based on the keylookup graph
        index_fields = [
            "drugbank.id",                      # Primary DrugBank identifier
            "drugbank.inchi_key",               # Structural identifier
            "drugbank.inchi",                   # Structural identifier
            "drugbank.smiles",                  # Structural identifier
            "drugbank.xrefs.chebi",             # ChEBI cross-reference
            "drugbank.xrefs.chembl",            # ChemBL cross-reference
            "drugbank.xrefs.pubchem.cid",       # PubChem cross-reference
            "drugbank.unii",                    # UNII identifier
            "drugbank.cas_number",              # CAS registry number
            "drugbank.name",                    # Drug name lookup
            "drugbank.products.ndc_product_code"  # NDC product codes
        ]

        # All except NDC (handled separately)
        for idxname in index_fields[:-1]:
            self.logger.info("Indexing '%s'" % idxname)
            # background=true or it'll lock the whole database...
            self.collection.create_index(
                [(idxname, pymongo.HASHED)], background=True)

        # NDC codes: hashed index won't support arrays, use standard index
        self.logger.info("Indexing 'drugbank.products.ndc_product_code'")
        self.collection.create_index("drugbank.products.ndc_product_code",
                                     background=True)

    @classmethod
    def get_mapping(cls):
        """return mapping information for drugbank"""
        return drugbank_full_mapping
