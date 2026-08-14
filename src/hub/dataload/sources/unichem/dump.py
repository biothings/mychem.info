from biothings.hub.dataload.dumper import FTPDumper
from biothings.utils.common import uncompressall
from config import DATA_ARCHIVE_ROOT
import os.path

import biothings
import config
biothings.config_for_app(config)


class Unichem_biothings_sdkDumper(FTPDumper):

    SRC_NAME = "unichem"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ebi.ac.uk'
    CWD_DIR = '/pub/databases/chembl/UniChem/legacy/oracleDumps'
    SCHEDULE = "0 6 * * *"
    UNCOMPRESS = True
    MAX_PARALLEL_DUMP = 1

    def get_newest_info(self):
        """Get the release number of the most recent dump directory"""
        # get list of directories
        releases = self.client.nlst()
        # remove alpha characters from direcotry names, leaving only numbers
        releases = [x[4:] for x in releases if x.startswith("UDRI")]
        # sort items based on UDRI number - highest is most recent
        releases = sorted(releases, key=int)
        # get the last item in the list, which is the latest version
        self.release = releases[-1]

    def new_release_available(self):
        """Determine if newest release needs to be downloaded"""
        # try checking release of version already downloaded
        current_release = (self.src_doc or {}).get("download", {}).get("release")
        if not current_release or int(self.release) > int(current_release):
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        """Add files to dump list for downloading"""
        self.get_newest_info()
        new_release_available = self.new_release_available()
        for fn in ["UC_SOURCE.txt.gz", "UC_STRUCTURE.txt.gz", "UC_XREF.txt.gz"]:
            local_file = os.path.join(self.new_data_folder, fn)
            uncompressed_file = os.path.splitext(local_file)[0]
            # add file to dump list if forced download, if path to local file doesnt exist,
            # or if there is a new release available
            local_file_exists = os.path.exists(local_file) or os.path.exists(uncompressed_file)
            if force or not local_file_exists or new_release_available:
                path = f"{self.CWD_DIR}/UDRI{self.release}/{fn}"
                self.to_dump.append({"remote": path, "local": local_file})

    def post_dump(self, *args, **kwargs):
        """After download/dump, uncompress the downloaded .gz files"""
        # UNCOMPRESS set to True
        if self.__class__.UNCOMPRESS:
            self.logger.info("Uncompress all archive files in '%s'" %
                             self.new_data_folder)
            uncompressall(self.new_data_folder)
