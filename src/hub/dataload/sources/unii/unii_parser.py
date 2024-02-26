import pandas as pd
from biothings.utils.dataload import int_convert


def load_data(input_file):
    try:
        unii = pd.read_csv(input_file, sep='\t', low_memory=False, dtype=str)
    except UnicodeDecodeError:
        unii = pd.read_csv(input_file, sep='\t', low_memory=False, dtype=str, encoding='windows-1252')
    
    unii.rename(columns={'MF': 'molecular_formula',
                         'PT': 'preferred_term',
                         'RN': 'registry_number'}, inplace=True)
    unii.columns = unii.columns.str.lower()

    # half of them don't have inchikeys
    # set the primary key to inchikey and fill in missing ones with unii
    unii['_id'] = unii.inchikey
    unii['_id'].fillna(unii.unii, inplace=True)

    dupes = set(unii._id) - set(unii._id.drop_duplicates(False))
    records = [{k: v for k, v in record.items() if pd.notnull(v)} for record in unii.to_dict("records") if record['_id'] not in dupes]
    records = [{'_id': record['_id'], 'unii': record} for record in records]
    # take care of a couple cases with identical inchikeys
    for dupe in dupes:
        dr = unii.query("_id == @dupe").to_dict("records")
        dr = [{k: v for k, v in record.items() if pd.notnull(v)} for record in dr]
        records.append({'_id': dupe, 'unii': dr})
    for record in records:
        if isinstance(record['unii'], dict):
            del record['unii']['_id']
        else:
            for subr in record['unii']:
                del subr['_id']

        # convert fields to integer
        record = int_convert(record, include_keys=['unii.pubchem'])

        yield record


if __name__ == "__main__":
    """For standalone debugging"""

    from glob import glob
    import json
    import sys

    # Add config directory to path
    sys.path.append("../../../../")

    from unii_dump import UniiDumper

    dumper = UniiDumper()
    dumper.get_latest_release()
    dumper.create_todump_list()

    input_file = glob(dumper.new_data_folder + "/*Records*.txt")[0]

    for rec in load_data(input_file):
        print(json.dumps(rec, indent=2))
