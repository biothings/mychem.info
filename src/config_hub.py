#############
# HUB VARS  #
#############

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
