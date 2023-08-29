import os
import os.path
import sys
import time
import bs4

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper


class DrugBankDumper(HTTPDumper):
    """
    DrugBank requires to sign-in before downloading a file. This dumper
    will just monitor new versions and report when a new one is available
    """

    SRC_NAME = "drugbank"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    AUTO_UPLOAD = False # it's still manual, so upload won't have the 

    SCHEDULE = "0 12 * * *"
    VERSIONS_URL = "https://www.drugbank.ca/releases"

    def create_todump_list(self,force=False,**kwargs):
        res = self.client.get(self.VERSIONS_URL)
        html = bs4.BeautifulSoup(res.text,"lxml")
        table = html.findAll(attrs={"class":"table-bordered"})
        assert len(table) == 1, "Expecting one table element, got %s" % len(table)
        table = table.pop()
        # the very first element in the table contains the latest version
        version = table.find("tbody").find("tr").find("td").text
        if force or not self.src_doc or (self.src_doc and self.src_doc.get("download",{}).get("release") < version):
            self.release = version # new_data_folder can be generated
            self.logger.info("DrugBank, new release '%s' available, please download it from " % version + \
                    "https://www.drugbank.ca/releases and put the file in folder '%s'. " % self.new_data_folder + \
                    "Once downloaded, run upload('drugbank') from the hub command line",
                    extra={"notify":True})
            local = os.path.join(self.new_data_folder,"releases")
            self.to_dump.append({"remote":self.VERSIONS_URL, "local":local})

