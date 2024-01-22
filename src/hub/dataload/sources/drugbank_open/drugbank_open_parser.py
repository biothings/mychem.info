import csv


def load_data(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)

        # Skip the header row
        next(reader)

        for row in reader:
            # Use InChI Key as the ID if it exists, else use DrugBank ID
            if row[6]:
                _id = row[6]
            else:
                _id = row[0]

            # Create a dictionary for each drug with fields parsed from the CSV
            drug_dict = {
                "_id": _id,
                "drugbank": {
                    "id": row[0],  # DrugBank ID
                    # Split Accession Numbers into a list
                    "accession_number": row[1].split(" | "),
                    "name": row[2],  # Common name
                    "cas": row[3],  # CAS number
                    "unii": row[4],  # UNII
                    # Split synonyms into a list if they exist, else assign an empty list
                    "synonyms": [synonym.strip() for synonym in row[5].split(" | ")] if row[5] else [],
                    # InChI Key (if the row has this field)
                    "inchi_key": row[6] if len(row) > 6 else None
                }
            }
            # Yield each drug dictionary one by one
            yield drug_dict

# Sample Row:
# DrugBank ID	Accession Numbers	Common name	CAS	UNII	Synonyms	Standard InChI Key
# DB00001	BIOD00024 | BTD00024	Lepirudin	138068-37-8	Y43GF64R34	[Leu1, Thr2]-63-desulfohirudin | Desulfatohirudin | Hirudin variant-1 | Lepirudin | Lepirudin recombinant | R-hirudin
