import gzip
import importlib.util
import json
from pathlib import Path

import pandas as pd


PARSER_PATH = (
    Path(__file__).parents[1]
    / "hub/dataload/sources/fda_orphan_drug/fda_orphan_drug_parser.py"
)


def load_parser_module():
    spec = importlib.util.spec_from_file_location("fda_orphan_drug_parser", PARSER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fda_export_reuses_recovered_identifiers(tmp_path):
    parser = load_parser_module()
    reference_file = tmp_path / "reference.json.gz"
    with gzip.open(reference_file, "wt", encoding="utf-8") as output:
        json.dump(
            [
                {
                    "_id": "AAAAAAAAAAAAAA-BBBBBBBBBB-C",
                    "fda_orphan_drug": [
                        {
                            "inchikey": "AAAAAAAAAAAAAA-BBBBBBBBBB-C",
                            "pubchem_cid": 123,
                            "generic_name": "Example drug",
                            "designated_date": "2020-01-02",
                            "orphan_designation": {
                                "original_text": "Treatment of condition one",
                                "umls": "C0000001",
                                "parsed_text": "Condition one",
                            },
                        }
                    ],
                }
            ],
            output,
        )

    columns = {
        "Trade Name": None,
        "Orphan Designation Status": "Designated",
        "FDA Orphan Approval Status": "Not FDA Approved for Orphan Indication",
        "Approved Labeled Indication": None,
        "Marketing Approval Date": None,
        "Exclusivity End Date": None,
        "Exclusivity Protected Indication *  (Shown for approvals from Jan. 1, 2013, to the present)": None,
        "Sponsor Company": "Example Sponsor",
        "Sponsor Address 1": "100 Main Street",
        "Sponsor Address 2": None,
        "Sponsor City": "Example City",
        "Sponsor State": "California",
        "Sponsor Zip": "' 90000 '",
        "Sponsor Country": "United States",
    }
    data = pd.DataFrame(
        [
            {
                **columns,
                "Generic Name": "Example drug",
                "Date Designated": "01/02/2020",
                "Orphan Designation": "Treatment of condition one",
            },
            {
                **columns,
                "Generic Name": "Example drug",
                "Date Designated": "03/04/2026",
                "Orphan Designation": "Treatment of condition two",
            },
            {
                **columns,
                "Generic Name": "Unmatched therapy",
                "Date Designated": "05/06/2026",
                "Orphan Designation": "Treatment of condition three",
            },
        ]
    )
    input_file = tmp_path / "fda_orphan_drug.xls"
    data.to_html(input_file, index=False)

    documents = list(parser.load_data(input_file, reference_file))

    assert len(documents) == 1
    assert documents[0]["_id"] == "AAAAAAAAAAAAAA-BBBBBBBBBB-C"
    records = documents[0]["fda_orphan_drug"]
    assert [record["designated_date"] for record in records] == [
        "2020-01-02",
        "2026-03-04",
    ]
    assert all(record["pubchem_cid"] == 123 for record in records)
    assert records[0]["orphan_designation"]["umls"] == "C0000001"
    assert "umls" not in records[1]["orphan_designation"]
    assert records[0]["sponsor"] == (
        "Example Sponsor|100 Main Street|Example City|California|90000|United States"
    )
