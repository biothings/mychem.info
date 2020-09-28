import os
import time
import ftplib

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import FTPDumper, DumperException


class PubChemDumper(FTPDumper):

    SRC_NAME = "pubchem"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
    CWD_DIR = '/pubchem/Compound/CURRENT-Full/XML'
    ARCHIVE = False
    SCHEDULE = "0 12 * * *"
    # MAX_PARALLEL_DUMP = 5

    VERSION_DIR = '/pubchem/Compound/Monthly'

    def get_release(self):
        try:
            self.client.cwd(self.__class__.VERSION_DIR)
            releases = sorted(self.client.nlst())
            if len(releases) == 0:
                raise DumperException("Can't any release information in '%s'" % self.__class__.VERSION_DIR)
            self.release = releases[-1]
        finally:
            self.client.cwd(self.__class__.CWD_DIR)

    def new_release_available(self):
        current_release = self.src_doc.get("download",{}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        self.logger.info("HELLO")
        self.get_release()
        if force or self.new_release_available():
            # get list of files to download
            remote_files = self.client.nlst()
            for remote in remote_files:
                try:
                    local = os.path.join(self.new_data_folder,remote)
                    if not os.path.exists(local) or self.remote_is_better(remote,local):
                        self.to_dump.append({"remote": remote,"local":local})
                except ftplib.error_temp as e:
                    self.logger.debug("Recycling FTP client because: '%s'" % e)
                    self.release_client()
                    self.prepare_client()

