import datetime
import os
import re

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

    def get_latest_release(self):
        res = self.client.get(self.__class__.HOMEPAGE_URL)
        # Raise error if status is not 200
        res.raise_for_status()
        # Parse the html for the text in the first 'div' element under the archive accordion
        html = bs4.BeautifulSoup(res.text, 'lxml')
        archive = html.find("div", attrs={"class": "usa-accordion__content usa-prose"})
        ################################################################################################
        # Try to find the version number.
        # If something is broken, it is  most likely this regex.
        # The  class of the element changes often with website updates.
        ################################################################################################
        link_element = archive.find("a", attrs={"class": re.compile("styles__Styled*")})
        if link_element:
            version = link_element.text
        else:
            raise DumperException("Could not parse the version number from website.")
        try:
            latest = datetime.date.strftime(dtparser.parse(version), "%Y-%m-%d")
            return latest
        except Exception as e:
            raise DumperException("Can't find or parse date from URL '%s': %s" % (self.__class__.HOMEPAGE_URL, e))

    def create_todump_list(self, force=False, **kwargs):
        self.release = self.get_latest_release()
        if force or not self.src_doc or (self.src_doc and self.src_doc.get("download", {}).get("release") < self.release):
            data_url = self.__class__.HOMEPAGE_URL + "/{}/UNII_Data_{}.zip".format(self.release, self.release.replace("-", ""))
            local = os.path.join(self.new_data_folder, self.release + ".zip")
            self.to_dump.append({"remote": data_url, "local": local})

    def post_dump(self, *args, **kwargs):
        unzipall(self.new_data_folder)
