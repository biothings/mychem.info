import logging

import pandas as pd
from biothings.utils.dataload import int_convert
from biothings_client import get_client

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def caching_ncit_descriptions(ncit_ids):
    """cache ncit descriptions for all unii.ncit IDs"""
    # if not ncit_ids:
    return {}

    ncit_api = get_client(url="https://biothings.ncats.io/ncit")
    ncit_ids = [f"NCIT:{ncit}" for ncit in ncit_ids]
    ncit_res = ncit_api.getnodes(ncit_ids, fields="def")
    ncit_def_d = {}
    for hit in ncit_res:
        if hit.get("def"):
            ncit_def = hit["def"]
            if ncit_def.startswith('"') and ncit_def.endswith('" []'):
                ncit_def = ncit_def[1:-4]
            ncit_def_d[hit["_id"].replace("NCIT:", "")] = ncit_def
    return ncit_def_d


def load_data(input_file):
    try:
        unii = pd.read_csv(input_file, sep='\t', low_memory=False, dtype=str)
    except UnicodeDecodeError:
        unii = pd.read_csv(input_file, sep='\t', low_memory=False,
                           dtype=str, encoding='windows-1252')

    unii.rename(columns={'MF': 'molecular_formula',
                         'PT': 'preferred_term',
                         'RN': 'registry_number'}, inplace=True)
    unii.columns = unii.columns.str.lower()

    # Set the primary key to the normalized inchikey and fallback on pubchem then unii
    unii['_id'] = unii.inchikey
    unii['_id'].fillna(unii.pubchem, inplace=True)
    unii['_id'].fillna(unii.unii, inplace=True)

    # Extract all unique ncit IDs
    ncit_ids = unii["ncit"].dropna().unique().tolist()
    ncit_descriptions = caching_ncit_descriptions(ncit_ids)

    dupes = set(unii._id) - set(unii._id.drop_duplicates(keep=False))
    records = [{k: v for k, v in record.items() if pd.notnull(v)}
               for record in unii.to_dict("records") if record['_id'] not in dupes]
    records = [{'_id': record['_id'], 'unii': record} for record in records]
    # take care of a couple cases with identical inchikeys
    for dupe in dupes:
        dr = unii.query("_id == @dupe").to_dict("records")
        dr = [{k: v for k, v in record.items() if pd.notnull(v)}
              for record in dr]
        records.append({'_id': dupe, 'unii': dr})
    for record in records:
        if 'ncit' in record['unii']:
            ncit_id = record['unii']['ncit']
            if ncit_id in ncit_descriptions:
                record['unii']['ncit_description'] = ncit_descriptions[ncit_id]
        if isinstance(record['unii'], dict):
            del record['unii']['_id']
            if 'display name' in record['unii']:
                record['unii']['display_name'] = record['unii'].pop(
                    'display name').strip()
        else:
            for subr in record['unii']:
                del subr['_id']
                if 'display name' in subr:
                    subr['display_name'] = subr.pop('display name').strip()

        record = int_convert(record, include_keys=['unii.pubchem'])

        yield record


if __name__ == "__main__":
    """For standalone debugging"""

    import json
    import sys
    from glob import glob

    # Add config directory to path
    sys.path.append("../../../../")

    from unii_dump import UniiDumper

    dumper = UniiDumper()
    dumper.get_latest_release()
    dumper.create_todump_list()

    input_file = glob(dumper.new_data_folder + "/*Records*.txt")[0]

    for rec in load_data(input_file):
        print(json.dumps(rec, indent=2))
