import os
import os.path
import ftplib
import glob
import shutil
import subprocess

import biothings
import config
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
    MAX_PARALLEL_DUMP = 2

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
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        self.get_release()
        failed_list = os.path.join(self.new_data_folder, "failed_dump.list")
        if self.new_release_available():
            # It's a new release, so make sure we remove failed file list and dump all.
            if os.path.exists(failed_list):
                os.remove(failed_list)
        # Check if any files failed in a previous dump
        if force and os.path.exists(failed_list):
            with open(failed_list, 'r') as f:
                failed_files = f.read().splitlines()
                self.logger.info("Found %s failed files in previous dump, will dump them again", len(failed_files))
                # Also store the filename without the .md5 extension
                failed_files += [f[:-4] for f in failed_files]
                self.to_dump = [{'remote': f, 'local': os.path.join(self.new_data_folder, f)} for f in failed_files]
        elif force or self.new_release_available():
            # get list of files to download
            remote_files = self.client.nlst()
            remote_files_set = set()
            for remote in remote_files:
                remote_files_set.add(remote)
                try:
                    local = os.path.join(self.new_data_folder, remote)
                    if not os.path.exists(local) or self.remote_is_better(remote, local):
                        self.to_dump.append({"remote": remote, "local": local})
                except ftplib.error_temp as e:
                    self.logger.debug("Recycling FTP client because: '%s'" % e)
                    self.release_client()
                    self.prepare_client()
            self.to_delete = []  # reset anyways
            base_dir = self.new_data_folder
            for dirpath, dirnames, filenames in os.walk(base_dir, topdown=False):
                # WARNING: this adds all directories for deletion as long as it is
                # or will be empty, because we assume are NO DIRECTORY STRUCTURE
                # on the remote and that's why NLST was used to populate
                # `remote_files` in the first place. If that ever changes this is
                # a trivial fix anyways.
                to_remove = set()
                for filename in filenames:
                    real_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(real_path, base_dir)
                    if rel_path in remote_files_set:
                        pass
                    else:
                        self.to_delete.append(rel_path)
                        to_remove.add(filename)
                if not (set(filenames) - to_remove):  # empty
                    self.to_delete.append(os.path.relpath(dirpath, base_dir))

    def post_dump(self, *args, **kwargs):
        '''Validate downloaded files'''
        if not self.ARCHIVE:
            if hasattr(self, 'post_dump_delete_files'):
                self.logger.debug("Invoking delete files function to remove files "
                                  "not on remote")
                self.post_dump_delete_files()
            else:
                self.logger.debug("Not invoking delete because parent class does not "
                                  "have the method")

        self.logger.debug("Start validating downloaded files...")
        cmd = shutil.which('md5sum')
        if cmd:
            old = os.path.abspath(os.curdir)
            os.chdir(self.new_data_folder)
            try:
                failed_list = os.path.join(self.new_data_folder, "failed_dump.list")
                if os.path.exists(failed_list):
                    # If we have a failed dump list, only check md5sum of files that failed
                    with open(failed_list, 'r') as f:
                        md5_files = f.read().splitlines()
                else:
                    md5_files = glob.glob("*.md5")
                failed_files = []
                if md5_files:
                    for md5_file in md5_files:
                        cmd = ["md5sum", "-c", md5_file]
                        self.logger.debug("\tValidating md5 checksum for: %s", md5_file)
                        try:
                            subprocess.check_call(cmd)
                        except subprocess.SubprocessError:
                            self.logger.error("Failed to validate: {}".format(md5_file))
                            failed_files.append(md5_file)
                    if failed_files:
                        err_msg = "Failed to validate {} md5 file(s):\n{}".format(
                            len(failed_files),
                            '\n'.join(["\t" + fn for fn in failed_files[:10]])    # only display top 10 if it's a long list
                        )
                        with open(failed_list, 'w') as f:
                            f.write('\n'.join(os.path.basename(failed_files)))
                        raise DumperException(err_msg)
                    else:
                        self.logger.debug("All %s files are validated.", len(md5_files))
                        # Delete failed dump list if it exists
                        if os.path.exists(failed_list):
                            os.remove(failed_list)
                else:
                    self.logger.debug("No *.md5 file(s) found! File validation is skipped.")
            finally:
                os.chdir(old)
        else:
            self.logger.warning('"md5sum" is not found in the PATH! File validation is skipped.')
