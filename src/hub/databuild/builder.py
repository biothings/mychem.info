import biothings.hub.databuild.builder as builder
import biothings.utils.mongo as mongo


class MyChemDataBuilder(builder.DataBuilder):

    def get_stats(self, sources, job_manager):
        self.stats = super(MyChemDataBuilder, self).get_stats(
            sources, job_manager)
        tgt = mongo.get_target_db()[self.target_name]
        self.stats["total"] = tgt.count()
        return self.stats
