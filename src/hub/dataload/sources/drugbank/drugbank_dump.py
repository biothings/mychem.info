import os

import bs4
from biothings.hub.dataload.dumper import HTTPDumper
from biothings.utils.common import unzipall
from config import DATA_ARCHIVE_ROOT


class DrugBankDumper(HTTPDumper):

    SRC_NAME = "drugbank"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SCHEDULE = "0 12 * * *"
    VERSIONS_URL = "https://go.drugbank.com/releases"

    def get_latest_release(self):
        res = self.client.get(self.VERSIONS_URL)
        res.raise_for_status()
        html = bs4.BeautifulSoup(res.text, "lxml")
        table = html.findAll(attrs={"class": "table-bordered"})
        assert len(table) == 1, f"Expecting one element, got {len(table)}"
        table = table.pop()
        # The very first element in the table contains the latest version
        version = table.find("tbody").find("tr").find("td").text
        return version

    def create_todump_list(self, force=False):
        self.release = self.get_latest_release()
        if force or not self.src_doc or (self.src_doc and self.src_doc.get(
                "download", {}).get("release") < self.release):
            remote_url = self.VERSIONS_URL + \
                "/{}/downloads/all-drugbank-vocabulary".format(
                    self.release.replace(".", "-")
                )
            local = os.path.join(self.new_data_folder,
                                 "all_drugbank_vocabulary.zip")
            self.to_dump.append({"remote": remote_url, "local": local})

    def post_dump(self, *args, **kwargs):
        unzipall(self.new_data_folder)
