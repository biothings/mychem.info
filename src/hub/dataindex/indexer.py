from copy import deepcopy

from biothings.hub.dataindex.indexer import Indexer

DEFAULT_INDEX_MAPPINGS = {
    "properties": {
        "all": {"type": "text"},
        "name": {
            "type": "text",
            "fields": {
                "raw": {
                    "type": "keyword",
                    "ignore_above": 128,
                    "normalizer": "keyword_lowercase_normalizer"
                }
            },
            "copy_to": "all"
        }
    }
}


class MyChemIndexer(Indexer):
    def __init__(self, build_doc, indexer_env, index_name):
        super().__init__(build_doc, indexer_env, index_name)

        new_mappings = deepcopy(DEFAULT_INDEX_MAPPINGS)

        self.es_index_mappings["properties"].update(
            new_mappings["properties"])

        self.logger.debug("Updated Index mappings: %s",
                          dict(self.es_index_mappings))
