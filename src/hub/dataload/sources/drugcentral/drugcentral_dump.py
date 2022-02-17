import os

import biothings
import config

biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import DummyDumper


class DrugCentralDumper(DummyDumper):

    SRC_NAME = "drugcentral"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
