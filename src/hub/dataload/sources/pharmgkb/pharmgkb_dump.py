import os, sys, re, time
import bs4
import dateutil.parser as dtparser
from datetime import datetime
import requests

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import unzipall


class PharmGkbDumper(LastModifiedHTTPDumper):

    SRC_NAME = "pharmgkb"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = ["https://api.pharmgkb.org/v1/download/file/data/drugs.zip"]
    #SCHEDULE = "0 12 * * *"

    def post_dump(self, *args, **kwargs):
        unzipall(self.new_data_folder)
