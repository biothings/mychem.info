import os, sys, re, time
import bs4
import dateutil.parser as dtparser
from datetime import datetime
import requests

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import unzipall


class NDCDumper(LastModifiedHTTPDumper):

    SRC_NAME = "ndc"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = ["http://www.accessdata.fda.gov/cder/ndctext.zip"]
    #SCHEDULE = "0 12 * * *"

    def post_dump(self, *args, **kwargs):
        unzipall(self.new_data_folder)
