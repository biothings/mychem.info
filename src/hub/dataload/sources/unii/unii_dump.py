import datetime
import os
import re
from urllib.parse import urljoin

import bs4
import dateutil.parser as dtparser
from biothings.hub.dataload.dumper import DumperException, HTTPDumper
from biothings.utils.common import unzipall

from config import DATA_ARCHIVE_ROOT


class UniiDumper(HTTPDumper):

    SRC_NAME = "unii"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SCHEDULE = "0 12 * * *"
    HOMEPAGE_URL = "https://precision.fda.gov/uniisearch/archive"
    DATA_ARCHIVE_PATTERN = re.compile(
        r"archive/(?P<release>\d{4}-\d{2}-\d{2})/UNII_Data_\d{8}\.zip$"
    )
    LAST_UPDATED_PATTERN = re.compile(
        r"Last Updated on\s+(?P<version>[A-Za-z]+\s+\d{1,2},\s+\d{4})"
    )

    def get_latest_release_info(self):
        res = self.client.get(self.__class__.HOMEPAGE_URL)
        res.raise_for_status()

        html = bs4.BeautifulSoup(res.text, "lxml")
        releases = []

        # Prefer explicit archive download URLs over CSS selectors or layout.
        for link in html.find_all("a", href=True):
            match = self.__class__.DATA_ARCHIVE_PATTERN.search(link["href"])
            if match:
                releases.append(
                    (
                        match.group("release"),
                        urljoin(self.__class__.HOMEPAGE_URL, link["href"]),
                    )
                )

        if releases:
            return max(releases, key=lambda item: item[0])

        # Fall back to the human-readable release stamp if needed.
        version_match = self.__class__.LAST_UPDATED_PATTERN.search(
            html.get_text(" ", strip=True)
        )
        if version_match:
            latest = datetime.date.strftime(
                dtparser.parse(version_match.group("version")), "%Y-%m-%d"
            )
            return latest, urljoin(
                self.__class__.HOMEPAGE_URL, "archive/latest/UNII_Data.zip"
            )

        raise DumperException(
            "Could not parse the latest UNII release from website."
        )

    def get_latest_release(self):
        latest, _ = self.get_latest_release_info()
        return latest

    def create_todump_list(self, force=False, **kwargs):
        self.release, data_url = self.get_latest_release_info()
        current_release = None
        if self.src_doc:
            current_release = self.src_doc.get("download", {}).get("release")

        if force or not current_release or current_release < self.release:
            local = os.path.join(self.new_data_folder, self.release + ".zip")
            self.to_dump.append({"remote": data_url, "local": local})

    def post_dump(self, *args, **kwargs):
        unzipall(self.new_data_folder)
        unzipall(self.new_data_folder)
