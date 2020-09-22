import requests
import math
import logging

from biothings.utils.dataload import dict_sweep, unlist
# from biothings.hub.datatransform.datatransform_api import DataTransformMyChemInfo


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('%(asctime)s - \
    %(name)s - %(levelname)s - %(message)s')
logger_handler = logging.FileHandler('dgidb.log')
logger_handler.setLevel(logging.DEBUG)
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)

def count_total_docs():
    """
    Get the total number of documents in DGIdb.
    There is no specific API endpoint providing that.
    But the informaiton is embeded in the results returned from interaction endpoint
    """
    query_url = 'http://www.dgidb.org/api/v2/interactions?count=1&page=1'
    return requests.get(query_url).json()['_meta']['total_count']

def fetch_all_docs_from_api():
    """
    Fetch all DGIdb data from api and store it in a list
    use pagination
    return 500 docs each time
    """
    dgidb_docs = []
    # number of docs returned per API call
    doc_per_query = 500
    # get the total number of docs in DGIdb
    total_count = count_total_docs()
    template_url = 'http://www.dgidb.org/api/v2/interactions?count=' + str(doc_per_query) + '&page={page}'
    # use pagination to fetch all docs
    for i in range(1, math.ceil(total_count/500) + 1):
        query_url = template_url.replace('{page}', str(i))
        doc = requests.get(query_url).json()
        dgidb_docs += doc.get('records')
    # make sure all docs are fetched
    assert len(dgidb_docs) == total_count
    return dgidb_docs

def chembl2mychemid(chembl_id):
    template_url = "http://mychem.info/v1/query?q=chembl.molecule_chembl_id:{chembl_id}&fields=_id"
    query_url = template_url.replace('{chembl_id}', chembl_id)
    doc = requests.get(query_url).json()
    if doc.get('total') == 0:
        logger.info('This chembl id %s is not found in MyChem.', chembl_id)
        return chembl_id
    elif doc.get('total') == 1:
        return doc.get('hits')[0].get('_id')
    else:
        logger.info('This chembl id %s has >1 hits in MyChem.', chembl_id)
        mychem_ids = [_doc['_id'] for _doc in doc['hits']]
        return mychem_ids
"""
DGIdb api
"""


# @DataTransformMyChemInfo([('chembl', 'dgidb.chembl_id')], ['inchikey'])
def load_data():
    dgidb_docs = fetch_all_docs_from_api()
    for _doc in dgidb_docs:
        _doc['interaction_id'] = _doc.pop('id')
        _doc['_id'] = chembl2mychemid(_doc['chembl_id'])
        yield dict_sweep(unlist({'dgidb': _doc}), vals=[None, "", []])
