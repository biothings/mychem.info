#!/usr/bin/env python

import logging
import os
from functools import partial

import biothings
import biothings.hub.databuild.differ as differ
from biothings.hub import HubServer
from biothings.utils.version import set_versions

import config
import hub.dataload

app_folder, _src = os.path.split(os.path.split(
    os.path.split(os.path.abspath(__file__))[0])[0])
set_versions(config, app_folder)
biothings.config_for_app(config)


class MyChemHubServer(HubServer):

    def configure_build_manager(self):
        import biothings.hub.databuild.builder as builder

        from hub.databuild.builder import MyChemDataBuilder

        # set specific managers
        build_manager = builder.BuilderManager(
            builder_class=MyChemDataBuilder, job_manager=self.managers["job_manager"])
        build_manager.configure()
        self.managers["build_manager"] = build_manager
        self.logger.info("Using custom builder %s" % MyChemDataBuilder)

    def configure_sync_manager(self):
        from biothings.hub.databuild.syncer import (
            SyncerManager,
            ThrottledESJsonDiffSelfContainedSyncer,
            ThrottledESJsonDiffSyncer,
        )

        # prod
        sync_manager_prod = SyncerManager(
            job_manager=self.managers["job_manager"])
        sync_manager_prod.configure(klasses=[partial(ThrottledESJsonDiffSyncer, config.MAX_SYNC_WORKERS),
                                             partial(ThrottledESJsonDiffSelfContainedSyncer, config.MAX_SYNC_WORKERS)])
        self.managers["sync_manager"] = sync_manager_prod
        # test will access localhost ES, no need to throttle
        sync_manager_test = SyncerManager(
            job_manager=self.managers["job_manager"])
        sync_manager_test.configure()
        self.managers["sync_manager_test"] = sync_manager_test
        self.logger.info("Using custom syncer, prod(throttled): %s, test: %s" % (
            sync_manager_prod, sync_manager_test))

    def configure_commands(self):
        super().configure_commands()  # keep all originals...
        # ... and enrich
        self.commands["merge_demo"] = partial(
            self.managers["build_manager"].merge, "demo_drug")
        self.commands["es_sync_test"] = partial(self.managers["sync_manager_test"].sync, "es",
                                                target_backend=(config.INDEX_CONFIG["env"]["local"]["host"],
                                                                config.INDEX_CONFIG["env"]["local"]["index"][0]["index"],
                                                                config.INDEX_CONFIG["env"]["local"]["index"][0]["doc_type"]))
        self.commands["es_sync_prod"] = partial(self.managers["sync_manager"].sync, "es",
                                                target_backend=(config.INDEX_CONFIG["env"]["prod"]["host"],
                                                                config.INDEX_CONFIG["env"]["prod"]["index"][0]["index"],
                                                                config.INDEX_CONFIG["env"]["prod"]["index"][0]["doc_type"]))
        # self.commands["es_test"] = config.INDEX_CONFIG["env"]["test"]
        # self.commands["es_prod"] = config.INDEX_CONFIG["env"]["prod"]
        # self.commands["publish_diff"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER,s3_bucket=config.S3_DIFF_BUCKET)
        # self.commands["publish_diff_demo"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER + "-demo",
        #                                        s3_bucket=config.S3_DIFF_BUCKET + "-demo")
        # self.commands["publish_snapshot"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER)
        # self.commands["publish_snapshot_demo"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER + "-demo")


# pass explicit list of datasources (no auto-discovery)
server = MyChemHubServer(hub.dataload.__sources_dict__, name="MyChem.info")

# disable logging for verbose utilties
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('tornado.access').setLevel(logging.WARNING)

if __name__ == "__main__":
    server.start()
