import os
import os.path

import biothings
import bs4
from biothings.hub.dataload.dumper import HTTPDumper

import config
from config import DATA_ARCHIVE_ROOT

biothings.config_for_app(config)


class DrugBankFullDumper(HTTPDumper):
    """
    DrugBank requires to sign-in before downloading a file. This dumper
    will just monitor new versions and report when a new one is available
    """

    SRC_NAME = "drugbank_full"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    AUTO_UPLOAD = False  # it's still manual, so upload won't have the

    # SCHEDULE = "0 12 * * *"
    VERSIONS_URL = "https://www.drugbank.ca/releases"

    def create_todump_list(self, force=False, **kwargs):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        res = self.client.get(self.VERSIONS_URL, headers=headers)
        if res.status_code != 200:
            raise ValueError(f"Failed to fetch URL: {
                             self.VERSIONS_URL}, Status Code: {res.status_code}")

        html = bs4.BeautifulSoup(res.text, "lxml")
        table = html.find(
            "div", class_="download-table").find("table", class_="table-bordered")
        if not table:
            raise ValueError(
                "Expected table not found in the HTML response. Check the structure of the page.")

        version = table.find("tbody").find("tr").find("td").text.strip()
        if force or not self.src_doc or (self.src_doc and self.src_doc.get("download", {}).get("release") < version):
            self.release = version
            self.logger.info(
                "DrugBank, new release '%s' available, please download it from " % version +
                "https://www.drugbank.ca/releases and put the file in folder '%s'. " % self.new_data_folder +
                "Once downloaded, run upload('drugbank') from the hub command line",
                extra={"notify": True}
            )
            local = os.path.join(self.new_data_folder, "releases")
            self.to_dump.append({"remote": self.VERSIONS_URL, "local": local})
