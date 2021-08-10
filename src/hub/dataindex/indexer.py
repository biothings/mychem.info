import asyncio

from biothings.hub.dataindex.indexer import Indexer


class DrugIndexer(Indexer):
    pass

    # @asyncio.coroutine
    # def index(self, job_manager, steps=("pre", "index", "post"), batch_size=2500, ids=None, mode="index"):
    #     return super().index(job_manager, steps=steps, batch_size=batch_size, ids=ids, mode=mode)
