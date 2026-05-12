import os
import os.path
import re
from urllib.parse import urlparse

import requests
from biothings.hub.dataload.dumper import FTPDumper
from biothings.utils.common import gunzipall

from config import DATA_ARCHIVE_ROOT


class ChebiDumper(FTPDumper):

    SRC_NAME = "chebi"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ebi.ac.uk'
    # ChEBI 2.0 products live under /pub/databases/chebi/.
    # Legacy products remain under /pub/databases/chebi/archive/chebi_legacy/.
    CWD_DIR = '/pub/databases/chebi'

    README_URL = "https://ftp.ebi.ac.uk/pub/databases/chebi/SDF/README"
    README_URL_SCHEMES = {"https"}

    SCHEDULE = "0 12 * * *"

    @classmethod
    def get_readme_url(cls):
        parsed_url = urlparse(cls.README_URL)
        if parsed_url.scheme.lower() not in cls.README_URL_SCHEMES:
            raise ValueError(
                "README_URL must use one of the allowed schemes "
                f"{sorted(cls.README_URL_SCHEMES)}: {cls.README_URL}"
            )
        if not parsed_url.netloc:
            raise ValueError(
                f"README_URL must be an absolute URL: {cls.README_URL}"
            )
        return cls.README_URL

    def get_release(self):
        readme_url = self.__class__.get_readme_url()
        resp = requests.get(readme_url, timeout=20)
        resp.raise_for_status()
        readme_text = resp.text

        match = re.search(r"ChEBI\s+Release:\s*([0-9]+)", readme_text)
        if not match:
            raise ValueError(
                (
                    "Could not find 'ChEBI Release:' in "
                    f"{readme_url}"
                )
            )
        self.release = match.group(1)

    def new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        def append_todump(sub_dir, filename):
            work_dir = os.path.join(
                self.__class__.CWD_DIR, sub_dir)
            self.client.cwd(work_dir)

            remote = os.path.join(work_dir, filename)
            local = os.path.join(self.new_data_folder, filename)

            self.to_dump.append({"remote": remote, "local": local})

        self.get_release()
        if force or self.new_release_available():
            # get list of files to download
            append_todump("SDF", "chebi.sdf.gz")
            append_todump("ontology", "chebi_lite.obo.gz")

    def post_dump(self, *args, **kwargs):
        gunzipall(self.new_data_folder)
