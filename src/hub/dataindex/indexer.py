import logging
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
        self.logger.debug("Creating DrugIndexer")

        # Log the original es index mappings
        self.logger.debug("Original Index mappings: %s",
                          dict(self.es_index_mappings))

        # Create a deep copy of the default index mappings
        new_mappings = deepcopy(DEFAULT_INDEX_MAPPINGS)

        # Update the existing mappings with the new properties
        if "properties" in self.es_index_mappings:
            self.es_index_mappings["properties"].update(
                new_mappings["properties"])
        else:
            raise AttributeError(
                "Unexpected structure for es_index_mappings: missing 'properties'")

        # Log the updated es index mappings
        self.logger.debug("Updated Index mappings: %s",
                          dict(self.es_index_mappings))
