import os
import os.path
import re

import biothings
import config

biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper


class DrugBankFullDumper(HTTPDumper):
    """
    DrugBank requires to sign-in before downloading a file. This dumper
    will just monitor new versions and report when a new one is available
    """

    SRC_NAME = "drugbank_full"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    AUTO_UPLOAD = False  # it's still manual, so upload won't have the

    SCHEDULE = "0 12 * * *"
    VERSIONS_URL = "https://go.drugbank.com/releases/latest"

    def get_version(self):
        """Read the current release from DrugBank's latest-release page."""
        response = self.client.get(self.VERSIONS_URL)
        response.raise_for_status()
        match = re.search(r"/releases/(\d+-\d+-\d+)", response.url)
        if not match:
            match = re.search(r"/releases/(\d+-\d+-\d+)", response.text)
        if not match:
            raise ValueError(
                "Cannot determine the latest DrugBank release from %s" % response.url
            )
        return match.group(1).replace("-", ".")

    @staticmethod
    def version_key(version):
        return tuple(int(part) for part in version.split("."))

    def create_todump_list(self, force=False, **kwargs):
        version = self.get_version()
        current_release = (self.src_doc or {}).get("download", {}).get("release")
        release_is_newer = not current_release or self.version_key(
            version
        ) > self.version_key(current_release)

        if force or release_is_newer:
            self.release = version  # new_data_folder can be generated
            self.logger.info(
                "DrugBank, new release '%s' available, please download it from "
                "https://go.drugbank.com/releases and put the file in folder '%s'. "
                "Once downloaded, run upload('drugbank_full') from the hub command line",
                version,
                self.new_data_folder,
                extra={"notify": True},
            )
            local = os.path.join(self.new_data_folder, "release.html")
            self.to_dump.append({"remote": self.VERSIONS_URL, "local": local})
