from datetime import datetime

import biothings
import requests
from bs4 import BeautifulSoup

import config

biothings.config_for_app(config)

import os

import pandas as pd
from biothings.hub.dataload.dumper import HTTPDumper
from biothings.utils.common import gunzipall

from config import DATA_ARCHIVE_ROOT


class SiderDumper(HTTPDumper):
    SRC_NAME = "sider"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # View the latest release here: http://sideeffects.embl.de/download/
    SRC_URL = "http://sideeffects.embl.de"
    FILES_TO_DUMP = [
        "meddra_freq.tsv.gz",
        "meddra_all_se.tsv.gz",
        "meddra_all_indications.tsv.gz",
    ]

    def create_todump_list(self, force=False):
        if force or self.new_release_available():
            response = requests.get(self.SRC_URL + "/download/")
            soup = BeautifulSoup(response.content, "html.parser")
            download_links = [
                link.get("href")
                for link in soup.find_all("a")
                if link.get("href", "").endswith(".tsv.gz")
            ]
            self.release = datetime.now().strftime("%Y%m%d")
            for link in download_links:
                if os.path.basename(link) in self.FILES_TO_DUMP:
                    remote = self.SRC_URL + link
                    local = os.path.join(self.new_data_folder, os.path.basename(link))
                    self.to_dump.append({"remote": remote, "local": local})

    def post_dump(self, *args, **kwargs):
        gunzipall(self.new_data_folder)
        self.logger.info("Merging files")
        FREQ = os.path.join(self.new_data_folder, "meddra_freq.tsv")
        ALL_SE = os.path.join(self.new_data_folder, "meddra_all_se.tsv")
        ALL_INDICATIONS = os.path.join(
            self.new_data_folder, "meddra_all_indications.tsv"
        )
        MERGED = os.path.join(
            self.new_data_folder, "merged_freq_all_se_indications.tsv"
        )
        # merge first two files- side effect and side effect with frequency
        # add header to csv files
        df1 = pd.read_csv(FREQ, delimiter="\t")
        df1.columns = [
            "stitch_id(flat)",
            "stitch_id(stereo)",
            "umls_id(label)",
            "is_placebo",
            "desc_type",
            "lower",
            "upper",
            "meddra_type",
            "umls_id(meddra)",
            "se_name",
        ]
        df2 = pd.read_csv(ALL_SE, delimiter="\t")
        df2.columns = [
            "stitch_id(flat)",
            "stitch_id(stereo)",
            "umls_id(label)",
            "meddra_type",
            "umls_id(meddra)",
            "se_name",
        ]
        s1 = pd.merge(
            df1,
            df2,
            how="outer",
            on=[
                "stitch_id(flat)",
                "stitch_id(stereo)",
                "umls_id(label)",
                "meddra_type",
                "umls_id(meddra)",
                "se_name",
            ],
        )

        # merge above merged file with indication file
        df4 = pd.read_csv(ALL_INDICATIONS, delimiter="\t")
        df4.columns = [
            "stitch_id(flat)",
            "umls_id(label)",
            "method_of_detection",
            "concept_name",
            "meddra_type",
            "umls_id(meddra)",
            "concept_name(meddra)",
        ]
        s2 = pd.merge(
            s1,
            df4,
            how="outer",
            on=["stitch_id(flat)", "umls_id(label)", "meddra_type", "umls_id(meddra)"],
        )
        s3 = s2.sort_values("stitch_id(flat)")
        s3.to_csv(MERGED)
        self.logger.info("Files successfully merged, ready to be uploaded")
