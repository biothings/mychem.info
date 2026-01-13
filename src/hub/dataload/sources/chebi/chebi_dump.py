import os
import os.path
import posixpath

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

    # Keep local filenames stable for downstream code.
    SDF_REMOTE_NAME = 'chebi.sdf.gz'
    SDF_LOCAL_NAME = 'ChEBI_complete.sdf.gz'
    OBO_REMOTE_NAME = 'chebi_lite.obo.gz'
    OBO_LOCAL_NAME = 'chebi_lite.obo.gz'

    SCHEDULE = "0 12 * * *"

    def _mdtm(self, cwd_dir, filename):
        """Return FTP MDTM timestamp string (YYYYMMDDHHMMSS) or None."""
        try:
            self.client.cwd(cwd_dir)
            # MDTM <file> returns: '213 YYYYMMDDHHMMSS'
            resp = self.client.sendcmd(f"MDTM {filename}")
            if isinstance(resp, str) and resp.startswith('213 '):
                return resp.split(' ', 1)[1].strip()
        except Exception:
            return None
        return None

    def get_release(self):
        # Derive a monotonic release identifier from remote modification times.
        # This preserves the existing 'new release available' behavior without
        # relying on versioned folders.
        sdf_mdtm = self._mdtm(
            posixpath.join(self.__class__.CWD_DIR, 'SDF'),
            self.__class__.SDF_REMOTE_NAME,
        )
        obo_mdtm = self._mdtm(
            posixpath.join(self.__class__.CWD_DIR, 'ontology'),
            self.__class__.OBO_REMOTE_NAME,
        )
        self.release = max([x for x in [sdf_mdtm, obo_mdtm] if x] or ['0'])

    def new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        def append_todump(sub_dir, remote_filename, local_filename=None):
            work_dir = posixpath.join(self.__class__.CWD_DIR, sub_dir)
            self.client.cwd(work_dir)

            remote = posixpath.join(work_dir, remote_filename)
            local_name = local_filename or remote_filename
            local = os.path.join(self.new_data_folder, local_name)

            self.to_dump.append({"remote": remote, "local": local})

        self.get_release()
        if force or self.new_release_available():
            # ChEBI 2.0
            append_todump(
                "SDF",
                self.__class__.SDF_REMOTE_NAME,
                self.__class__.SDF_LOCAL_NAME,
            )
            append_todump(
                "ontology",
                self.__class__.OBO_REMOTE_NAME,
                self.__class__.OBO_LOCAL_NAME,
            )

    def post_dump(self, *args, **kwargs):
        gunzipall(self.new_data_folder)
