import os

from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from config import DATA_ARCHIVE_ROOT


class GSRSDumper(LastModifiedHTTPDumper):

    SRC_NAME = "gsrs"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = ["https://gsrs.ncats.nih.gov/downloads/dump-public-2023-12-14.gsrs"]
    SCHEDULE = "0 12 * * *"
