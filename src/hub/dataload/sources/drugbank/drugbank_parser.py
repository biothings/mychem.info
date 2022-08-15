from biothings.utils.dataload import dict_sweep, tabfile_feeder, unlist


def load_data(input_file):
    """
    input_file is a csv file with the following columns:
        1   DrugBank ID
        2   Accession Numbers
        3   Common name
        4   CAS
        5   UNII
        6   Synonyms
        7   Standard InChI Key
    """
    data = tabfile_feeder(input_file, header=0, sep=",")
    header = next(data)
    assert header == ["DrugBank ID", "Accession Numbers", "Common name",
                      "CAS", "UNII", "Synonyms", "Standard InChI Key"], \
        "Found unexpected header columns, check file for changes."

    for row in data:
        drugbank_id = row[0]
        accession_numbers = row[1].split(" | ")
        common_name = row[2]
        cas = row[3]
        unii = row[4]
        synonyms = row[5].split(" | ")
        inchikey = row[6]

        # drubank_id and common_name are required fields in the dataset
        assert drugbank_id and common_name, \
            "Missing drugbank_id or common_name in row: {}".format(row)

        # _id is set to inchikey, but if not available, set to drugbank_id
        _id = inchikey if inchikey else drugbank_id

        # Create dict for each row
        doc = {
            "_id": _id,
            "drugbank": {
                "id": drugbank_id,
                "accession_number": accession_numbers,
                "name": common_name,
                "cas_rn": cas,
                "unii": unii,
                "synonyms": synonyms,
                "inchikey": inchikey
            }
        }

        doc = unlist(doc)      # change lists with one element to string
        doc = dict_sweep(doc)  # remove empty keys
        yield doc


if __name__ == "__main__":
    import json
    import os
    import sys

    # Add config directory to path
    sys.path.append("../../../../")

    from drugbank_dump import DrugBankDumper

    dumper = DrugBankDumper()
    version = dumper.get_latest_release()
    dumper.create_todump_list()
    for rec in load_data(
            os.path.join(dumper.new_data_folder + '/drugbank vocabulary.csv')):
        # pass
        print(json.dumps(rec, indent=2))
