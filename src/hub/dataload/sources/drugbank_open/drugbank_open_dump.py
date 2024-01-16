import os
import os.path
import re

import biothings
import requests
from biothings.hub.dataload.dumper import HTTPDumper

import config
from config import DATA_ARCHIVE_ROOT

biothings.config_for_app(config)


class DrugBankOpenDumper(HTTPDumper):

    SRC_NAME = "drugbank"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    AUTO_UPLOAD = True

    SCHEDULE = "0 12 * * *"
    BASE_URL = "https://go.drugbank.com"
    DOWNLOAD_URL = BASE_URL + \
        "/releases/{version}/downloads/all-drugbank-vocabulary"
    VERSIONS_URL = "https://go.drugbank.com/releases/latest"

    def get_version(self):
        """
        Get the version information from the latest releases page.
        """
        response = requests.get(self.VERSIONS_URL)
        if response.status_code == 200:
            match = re.search(r"/releases/(\d+-\d+-\d+)", response.text)
            if match:
                return match.group(1)
        return None

    def create_todump_list(self, force=False, **kwargs):
        version = self.get_version()
        if not version:
            self.logger.error(
                "Cannot determine the latest version of DrugBank.")
            return

        if force or not self.src_doc or (self.src_doc and self.src_doc.get("download", {}).get("release") < version):
            self.release = version
            remote = self.DOWNLOAD_URL.format(version=version)
            local = os.path.join(self.new_data_folder,
                                 "all-drugbank-vocabulary.csv.zip")
            self.to_dump.append({"remote": remote, "local": local})
