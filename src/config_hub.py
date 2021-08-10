#############
# HUB VARS  #
#############
import logging
from biothings.utils.loggers import setup_default_log
from biothings.utils.configuration import ConfigurationError, ConfigurationDefault
import biothings.utils.jsondiff
import importlib
import os

DATA_HUB_DB_DATABASE = "drug_hubdb"                   # db containing the following (internal use)
DATA_SRC_MASTER_COLLECTION = 'src_master'             # for metadata of each src collections
DATA_SRC_DUMP_COLLECTION = 'src_dump'                 # for src data download information
DATA_SRC_BUILD_COLLECTION = 'src_build'               # for src data build information
DATA_SRC_BUILD_CONFIG_COLLECTION = 'src_build_config'  # for src data build configuration
DATA_PLUGIN_COLLECTION = 'data_plugin'                # for data plugins information
# for api information (running under hub control)
API_COLLECTION = 'api'
EVENT_COLLECTION = "event"
CMD_COLLECTION = "cmd"

# reporting diff results, number of IDs to consider (to avoid too much mem usage)
MAX_REPORTED_IDS = 1000
# for diff updates, number of IDs randomly picked as examples when rendering the report
MAX_RANDOMLY_PICKED = 10

# where to store info about processes launched by the hub
RUN_DIR = './run'

# Max queued jobs in job manager
# this shouldn't be 0 to make sure a job is pending and ready to be processed
# at any time (avoiding job submission preparation) but also not a huge number
# as any pending job will consume some memory).
MAX_QUEUED_JOBS = os.cpu_count() * 4

# Max number of *processes* hub can access to run jobs
HUB_MAX_WORKERS = int(os.cpu_count() / 4)
# max number of sync workers (when throttled). Default is all workers
MAX_SYNC_WORKERS = HUB_MAX_WORKERS

# Max memory usage before hub will prevent creating more jobs, in byte
# If None, no limit. It's a good practice to put a limit as the more processes
# are used, the more they consume memory even if nothing runs. With a limit, hub
# will recycle the process queue in order to limit the memory usage
HUB_MAX_MEM_USAGE = None

# compressed cache files
CACHE_FORMAT = "xz"

# Hub environment (like, prod, dev, ...)
# Used to generate remote metadata file, like "latest.json", "versions.json"
# If non-empty, this constant will be used to generate those url, as a prefix
# with "-" between. So, if "dev", we'll have "dev-latest.json", etc...
# "" means production
HUB_ENV = ""

# Hub name/icon url/version, for display purpose
HUB_NAME = "MyChem"
HUB_ICON = "http://biothings.io/static/img/mychem-logo-shiny.svg"

# Pre-prod/test ES definitions
INDEX_CONFIG = {
    "indexer_select": {
        # default
        None: "hub.dataindex.indexer.DrugIndexer",
    },
    "env": {
        "prod": {
            "host": "<PRODSERVER>:9200",
            "indexer": {
                    "args": {
                        "timeout": 300,
                        "retry_on_timeout": True,
                        "max_retries": 10,
                    },
            },
            "index": [{"index": "mydrugs_current", "doc_type": "drug"}],
        },
        "local": {
            "host": "localhost:9200",
            "indexer": {
                    "args": {
                        "timeout": 300,
                        "retry_on_timeout": True,
                        "max_retries": 10,
                    },
            },
            "index": [{"index": "mydrugs_current", "doc_type": "drug"}],
        },
    },
}


# Snapshot environment configuration
SNAPSHOT_CONFIG = {
    "env": {
        "prod": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "repository": {
                "name": "drug_repository-$(Y)",
                "type": "s3",
                "settings": {
                        "bucket": "<SNAPSHOT_BUCKET_NAME>",
                        "base_path": "mychem.info/$(Y)",  # per year
                        "region": "us-west-2",
                },
                "acl": "private",
            },
            "indexer": {
                # reference to INDEX_CONFIG
                "env": "local",
            },
            # when creating a snapshot, how long should we wait before querying ES
            # to check snapshot status/completion ? (in seconds)
            "monitor_delay": 60 * 5,
        },
        "demo": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "repository": {
                "name": "drug_repository-demo-$(Y)",
                "type": "s3",
                "settings": {
                        "bucket": "<SNAPSHOT_DEMO_BUCKET_NAME>",
                        "base_path": "mychem.info/$(Y)",  # per year
                        "region": "us-west-2",
                },
                "acl": "public",
            },
            "indexer": {
                # reference to INDEX_CONFIG
                "env": "local",
            },
            # when creating a snapshot, how long should we wait before querying ES
            # to check snapshot status/completion ? (in seconds)
            "monitor_delay": 10,
        }
    }
}

# Release configuration
# Each root keys define a release environment (test, prod, ...)
RELEASE_CONFIG = {
    "env": {
        "prod": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "release": {
                "bucket": "<RELEASES_BUCKET_NAME>",
                "region": "us-west-2",
                "folder": "mychem.info",
                "auto": True,  # automatically generate release-note ?
            },
            "diff": {
                "bucket": "<DIFFS_BUCKET_NAME>",
                "folder": "mychem.info",
                "region": "us-west-2",
                "auto": True,  # automatically generate diff ? Careful if lots of changes
            },
        },
        "demo": {
            "cloud": {
                "type": "aws",  # default, only one supported by now
                "access_key": None,
                "secret_key": None,
            },
            "release": {
                "bucket": "<RELEASES_BUCKET_NAME>",
                "region": "us-west-2",
                "folder": "mychem.info-demo",
                "auto": True,  # automatically generate release-note ?
            },
            "diff": {
                "bucket": "<DIFFS_BUCKET_NAME>",
                "folder": "mychem.info",
                "region": "us-west-2",
                "auto": True,  # automatically generate diff ? Careful if lots of changes
            },
        }
    }
}


SLACK_WEBHOOK = None

# SSH port for hub console
HUB_SSH_PORT = 7022
HUB_API_PORT = 7080

################################################################################
# HUB_PASSWD
################################################################################
# The format is a dictionary of 'username': 'cryptedpassword'
# Generate crypted passwords with 'openssl passwd -crypt'
HUB_PASSWD = {"guest": "9RKfd8gDuNf0Q"}

# cached data (it None, caches won't be used at all)
CACHE_FOLDER = None

# when publishing releases, specify the targetted (ie. required) standalone version
STANDALONE_VERSION = "standalone_v3"

# don't bother with elements order in a list when diffing,
# mygene optmized uploaders can't produce different results
# when parsing data (parallelization)
importlib.reload(biothings.utils.jsondiff)
biothings.utils.jsondiff.UNORDERED_LIST = True

########################################
# APP-SPECIFIC CONFIGURATION VARIABLES #
########################################
# The following variables should or must be defined in your
# own application. Create a config.py file, import that config_common
# file as:
#
#   from config_hub import *
#
# then define the following variables to fit your needs. You can also override any
# any other variables in this file as required. Variables defined as ValueError() exceptions
# *must* be defined
#
# To be defined at application-level:

# Individual source database connection
DATA_SRC_SERVER = ConfigurationError("Define hostname for source database")
DATA_SRC_PORT = ConfigurationError("Define port for source database")
DATA_SRC_DATABASE = ConfigurationError("Define name for source database")
DATA_SRC_SERVER_USERNAME = ConfigurationError(
    "Define username for source database connection (or None if not needed)")
DATA_SRC_SERVER_PASSWORD = ConfigurationError(
    "Define password for source database connection (or None if not needed)")

# Target (merged collection) database connection
DATA_TARGET_SERVER = ConfigurationError("Define hostname for target database (merged collections)")
DATA_TARGET_PORT = ConfigurationError("Define port for target database (merged collections)")
DATA_TARGET_DATABASE = ConfigurationError("Define name for target database (merged collections)")
DATA_TARGET_SERVER_USERNAME = ConfigurationError(
    "Define username for target database connection (or None if not needed)")
DATA_TARGET_SERVER_PASSWORD = ConfigurationError(
    "Define password for target database connection (or None if not needed)")

HUB_DB_BACKEND = ConfigurationError("Define Hub DB connection")
# Internal backend. Default to mongodb
# For now, other options are: mongodb, sqlite3, elasticsearch
# HUB_DB_BACKEND = {
#        "module" : "biothings.utils.sqlite3",
#        "sqlite_db_folder" : "./db",
#        }
# HUB_DB_BACKEND = {
#        "module" : "biothings.utils.mongo",
#        "uri" : "mongodb://localhost:27017",
#        #"uri" : "mongodb://user:passwd@localhost:27017", # mongodb std URI
#        }
# HUB_DB_BACKEND = {
#        "module" : "biothings.utils.es",
#        "host" : "localhost:9200",
#        }

# Path to a folder to store all downloaded files, logs, caches, etc...
DATA_ARCHIVE_ROOT = ConfigurationError(
    "Define path to folder which will contain all downloaded data, cache files, etc...")

# Path to a folder to store all 3rd party parsers, dumpers, etc...
DATA_PLUGIN_FOLDER = ConfigurationDefault(
    default="./plugins",
    desc="Define path to folder which will contain all 3rd party parsers, dumpers, etc...")

# this dir must be created manually
LOG_FOLDER = ConfigurationError("Define path to folder which will contain log files")
# Usually inside DATA_ARCHIVE_ROOT
#LOG_FOLDER = os.path.join(DATA_ARCHIVE_ROOT,'logs')

# Path to folder containing diff files
DIFF_PATH = ConfigurationError("Define path to folder which will contain output files from diff")
# Usually inside DATA_ARCHIVE_ROOT
#DIFF_PATH = os.path.join(DATA_ARCHIVE_ROOT,"diff")

# Path to folder containing release note files
RELEASE_PATH = ConfigurationError("Define path to folder which will contain output files from diff")
# Usually inside DATA_ARCHIVE_ROOT
#RELEASE_PATH = os.path.join(DATA_ARCHIVE_ROOT,"release")

# default hub logger
logger = ConfigurationDefault(
    default=logging,
    desc="Provide a default hub logger instance (use setup_default_log(name,log_folder)")
