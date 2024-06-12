from copy import deepcopy

from biothings.hub.dataindex.indexer import Indexer, IndexMappings

DEFAULT_INDEX_MAPPINGS = {
    "dynamic": "false",
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


class DrugIndexer(Indexer):
    def __init__(self, build_doc, indexer_env, index_name):
        super().__init__(build_doc, indexer_env, index_name)
        self.es_index_mappings = IndexMappings(
            deepcopy(DEFAULT_INDEX_MAPPINGS))
