import os
import sys
import time
import ftplib
import re
import pandas as pd

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import FTPDumper, DumperException
from biothings.utils.common import gunzipall


class SiderDumper(FTPDumper):

    SRC_NAME = "sider"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'xi.embl.de'
    CWD_DIR = '/SIDER'
    #SCHEDULE = "0 12 * * *"

    def get_release(self):
        # only dir with dates
        releases = sorted([d for d in self.client.nlst() if re.match("\d{4}-\d{2}-\d{2}",d)])
        if len(releases) == 0:
            raise DumperException("Can't any release information in '%s'" % self.__class__.VERSION_DIR)
        self.release = releases[-1]

    def new_release_available(self):
        current_release = self.src_doc.get("download",{}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        self.get_release()
        if force or self.new_release_available():
            # get list of files to download
            files = ["meddra_freq.tsv.gz","meddra_all_se.tsv.gz","meddra_all_indications.tsv.gz"]
            for one_file in files:
                remote = os.path.join(self.release,one_file)
                local = os.path.join(self.new_data_folder,one_file)
                if not os.path.exists(local) or self.remote_is_better(remote,local):
                    self.to_dump.append({"remote": remote,"local":local})

    def post_dump(self, *args, **kwargs):
        gunzipall(self.new_data_folder)
        self.logger.info("Merging files")
        FREQ = os.path.join(self.new_data_folder,"meddra_freq.tsv")
        ALL_SE = os.path.join(self.new_data_folder,"meddra_all_se.tsv")
        ALL_INDICATIONS = os.path.join(self.new_data_folder,"meddra_all_indications.tsv")
        MERGED = os.path.join(self.new_data_folder,"merged_freq_all_se_indications.tsv")
        #merge first two files- side effect and side effect with frequency
        #add header to csv files
        df1 = pd.read_csv(FREQ, delimiter='\t')
        df1.columns = ['stitch_id(flat)','stitch_id(stereo)','umls_id(label)','is_placebo',
                'desc_type','lower','upper','meddra_type','umls_id(meddra)','se_name']
        df2 = pd.read_csv(ALL_SE, delimiter='\t')
        df2.columns = ['stitch_id(flat)','stitch_id(stereo)','umls_id(label)','meddra_type',
                'umls_id(meddra)','se_name']
        s1 = pd.merge(df1, df2, how='outer',on=['stitch_id(flat)','stitch_id(stereo)','umls_id(label)','meddra_type','umls_id(meddra)','se_name'])

        #merge above merged file with indication file
        df4 = pd.read_csv(ALL_INDICATIONS,delimiter='\t')
        df4.columns =['stitch_id(flat)','umls_id(label)','method_of_detection','concept_name',
                'meddra_type','umls_id(meddra)','concept_name(meddra)']
        s2 = pd.merge(s1,df4,how='outer',on=['stitch_id(flat)','umls_id(label)','meddra_type','umls_id(meddra)'])
        s3 = s2.sort_values('stitch_id(flat)')
        s3.to_csv(MERGED)
        self.logger.info("Files successfully merged, ready to be uploaded")

