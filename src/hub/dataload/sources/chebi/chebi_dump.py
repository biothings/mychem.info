import os
import os.path
import re
import urllib.request

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

    SCHEDULE = "0 12 * * *"

    def get_release(self):
        with urllib.request.urlopen(
            self.__class__.README_URL, timeout=20
        ) as resp:
            readme_text = resp.read().decode("utf-8", errors="replace")

        match = re.search(r"ChEBI\s+Release:\s*([0-9]+)", readme_text)
        if not match:
            raise ValueError(
                (
                    "Could not find 'ChEBI Release:' in "
                    f"{self.__class__.README_URL}"
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
