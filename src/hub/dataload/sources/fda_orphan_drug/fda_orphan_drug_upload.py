import os

from hub.dataload.uploader import BaseDrugUploader

from .fda_orphan_drug_mapping import get_mapping
from .fda_orphan_drug_parser import load_data


class FDAOrphanDrugUploader(BaseDrugUploader):
    name = "fda_orphan_drug"
    __metadata__ = {
        "src_meta": {
            "url": "https://www.accessdata.fda.gov/scripts/opdlisting/oopd/",
            "license": "public domain",
        }
    }

    def load_data(self, data_folder):
        input_file = os.path.join(data_folder, "fda_orphan_drug.xls")
        return load_data(input_file)

    @classmethod
    def get_mapping(cls):
        return get_mapping()
