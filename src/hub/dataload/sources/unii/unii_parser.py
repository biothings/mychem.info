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
    if not ncit_ids:
        return {}

    ncit_api = get_client(url="https://biothings.ncats.io/ncit")
    ncit_ids = [f"NCIT:{ncit}" for ncit in ncit_ids]
    ncit_res = ncit_api.getnodes(ncit_ids, fields="definition")
    ncit_def_d = {}
    for hit in ncit_res:
        if hit.get("definition"):
            ncit_def = hit["definition"]
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

    # half of them don't have inchikeys
    # set the primary key to inchikey and fill in missing ones with unii
    unii['_id'] = unii.inchikey
    unii['_id'].fillna(unii.pubchem, inplace=True)
    unii['_id'].fillna(unii.unii, inplace=True)

    # Extract all unique ncit IDs
    ncit_ids = unii["ncit"].dropna().unique().tolist()
    ncit_descriptions = caching_ncit_descriptions(ncit_ids)

    dupes = set(unii._id) - set(unii._id.drop_duplicates(keep=False))
    records = [{k: v for k, v in record.items() if pd.notnull(v)}
               for record in unii.to_dict("records") if record['_id'] not in dupes]

    # Sanitize keylookup fields for non-duplicate records
    keylookup_fields = ['inchikey', 'smiles', 'pubchem', 'unii',
                        'preferred_term', 'drugcentral']
    for record in records:
        for field in keylookup_fields:
            if field in record and record[field] is not None:
                if not isinstance(record[field], (str, int, float)):
                    record[field] = str(record[field])

    records = [{'_id': record['_id'], 'unii': record} for record in records]
    # take care of a couple cases with identical inchikeys
    for dupe in dupes:
        dr = unii.query("_id == @dupe").to_dict("records")
        dr = [{k: v for k, v in record.items() if pd.notnull(v)}
              for record in dr]
        # Merge duplicate records for keylookup compatibility
        # For keylookup compatibility, we need a single dict structure
        merged_record = {}
        for record in dr:
            for key, value in record.items():
                if key not in merged_record:
                    merged_record[key] = value
                elif isinstance(merged_record[key], list):
                    if value not in merged_record[key]:
                        merged_record[key].append(value)
                elif merged_record[key] != value:
                    # Convert to list if values differ
                    merged_record[key] = [merged_record[key], value]

        # For keylookup fields, ensure we use single values, not lists
        # Take the first value if multiple exist
        keylookup_fields = ['inchikey', 'smiles', 'pubchem', 'unii',
                            'preferred_term', 'drugcentral']
        for field in keylookup_fields:
            if field in merged_record:
                if isinstance(merged_record[field], list):
                    # Take the first non-null value
                    merged_record[field] = next(
                        (v for v in merged_record[field]
                         if pd.notnull(v)), None)
                # Ensure the value is a simple string/number, not complex
                if (merged_record[field] is not None and
                        not isinstance(merged_record[field],
                                       (str, int, float))):
                    merged_record[field] = str(merged_record[field])

        records.append({'_id': dupe, 'unii': merged_record})
    for record in records:
        # Now record['unii'] is always a dict (we merged duplicates above)
        if 'ncit' in record['unii']:
            ncit_id = record['unii']['ncit']
            if ncit_id in ncit_descriptions:
                record['unii']['ncit_description'] = ncit_descriptions[ncit_id]

        # Clean up the record - check if _id exists before deleting
        if '_id' in record['unii']:
            del record['unii']['_id']
        if 'display name' in record['unii']:
            record['unii']['display_name'] = record['unii'].pop(
                'display name').strip()

        # convert fields to integer
        record = int_convert(record, include_keys=['unii.pubchem'])

        # Final sanitization of keylookup fields before yielding
        keylookup_fields = ['inchikey', 'smiles', 'pubchem', 'unii',
                            'preferred_term', 'drugcentral']
        for field in keylookup_fields:
            if field in record['unii'] and record['unii'][field] is not None:
                if not isinstance(record['unii'][field], (str, int, float)):
                    record['unii'][field] = str(record['unii'][field])
                # Also ensure no empty strings are used for lookups
                if record['unii'][field] == '':
                    record['unii'][field] = None

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
