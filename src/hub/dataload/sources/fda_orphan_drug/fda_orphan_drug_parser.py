import gzip
import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime

import pandas as pd


LOGGER = logging.getLogger(__name__)
REFERENCE_FILE = os.path.join(os.path.dirname(__file__), "reference.json.gz")
IDENTIFIER_FIELDS = ("pubchem_sid", "pubchem_cid", "inchikey")
SPONSOR_COLUMNS = (
    "Sponsor Company",
    "Sponsor Address 1",
    "Sponsor Address 2",
    "Sponsor City",
    "Sponsor State",
    "Sponsor Zip",
    "Sponsor Country",
)


def clean_text(value):
    if value is None or pd.isna(value):
        return None
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value or None


def normalized_text(value):
    return (clean_text(value) or "").casefold()


def normalized_date(value):
    value = clean_text(value)
    if not value:
        return None
    for date_format in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, date_format).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError("Unrecognized FDA orphan-drug date: %s" % value)


def record_signature(generic_name, designated_date, designation):
    return "\x1f".join(
        (
            normalized_text(generic_name),
            normalized_date(designated_date) or "",
            normalized_text(designation),
        )
    )


def reference_signature(record):
    orphan_designation = record.get("orphan_designation") or {}
    return record_signature(
        record.get("generic_name"),
        record.get("designated_date"),
        orphan_designation.get("original_text"),
    )


def load_reference(reference_file=REFERENCE_FILE):
    with gzip.open(reference_file, "rt", encoding="utf-8") as input_file:
        return json.load(input_file)


def build_reference_indexes(reference_documents):
    exact_matches = defaultdict(dict)
    generic_matches = defaultdict(dict)
    designation_matches = defaultdict(dict)

    for document in reference_documents:
        document_id = str(document["_id"])
        records = document["fda_orphan_drug"]
        if not isinstance(records, list):
            records = [records]

        for record in records:
            identifiers = {
                field: record[field]
                for field in IDENTIFIER_FIELDS
                if record.get(field) is not None
            }
            identity_key = json.dumps(
                [document_id, identifiers], sort_keys=True, ensure_ascii=False
            )
            identity = {"_id": document_id, "identifiers": identifiers}
            exact_identity = dict(identity)

            orphan_designation = record.get("orphan_designation") or {}
            enrichment = {
                field: orphan_designation[field]
                for field in ("umls", "parsed_text")
                if orphan_designation.get(field)
            }
            if enrichment:
                exact_identity["orphan_designation"] = enrichment
                designation_key = normalized_text(
                    orphan_designation.get("original_text")
                )
                enrichment_key = json.dumps(
                    enrichment, sort_keys=True, ensure_ascii=False
                )
                designation_matches[designation_key][enrichment_key] = enrichment

            exact_matches[reference_signature(record)][identity_key] = exact_identity
            generic_matches[normalized_text(record.get("generic_name"))][
                identity_key
            ] = identity

    return exact_matches, generic_matches, designation_matches


def get_sponsor(row):
    parts = []
    for column in SPONSOR_COLUMNS:
        value = clean_text(row.get(column))
        if value:
            parts.append(value.strip(" '"))
    return "|".join(filter(None, parts)) or None


def optional_column(row, column):
    value = clean_text(row.get(column))
    return value if value else None


def get_exclusivity_column(columns):
    matches = [
        column
        for column in columns
        if column.startswith("Exclusivity Protected Indication")
    ]
    if len(matches) != 1:
        raise ValueError(
            "Expected one FDA exclusivity-protected-indication column, found %s"
            % len(matches)
        )
    return matches[0]


def build_record(row, identifiers, orphan_enrichment, exclusivity_column):
    record = {
        **identifiers,
        "generic_name": clean_text(row["Generic Name"]),
        "designated_date": normalized_date(row["Date Designated"]),
        "designation_status": clean_text(row["Orphan Designation Status"]),
        "approval_status": clean_text(row["FDA Orphan Approval Status"]),
        "sponsor": get_sponsor(row),
        "orphan_designation": {
            "original_text": clean_text(row["Orphan Designation"]),
            **orphan_enrichment,
        },
        "trade_name": optional_column(row, "Trade Name"),
        "approved_labeled_indication": optional_column(
            row, "Approved Labeled Indication"
        ),
        "marketing_approval_date": normalized_date(row.get("Marketing Approval Date")),
        "exclusivity_end_date": normalized_date(row.get("Exclusivity End Date")),
        "exclusivity_protected_indication": optional_column(row, exclusivity_column),
    }
    return {key: value for key, value in record.items() if value is not None}


def load_data(input_file, reference_file=REFERENCE_FILE):
    tables = pd.read_html(input_file)
    if len(tables) != 1:
        raise ValueError(
            "Expected one table in the FDA Excel export, found %s" % len(tables)
        )

    data = tables[0]
    required_columns = {
        "Generic Name",
        "Date Designated",
        "Orphan Designation",
        "Orphan Designation Status",
        "FDA Orphan Approval Status",
        *SPONSOR_COLUMNS,
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError("FDA export is missing columns: %s" % sorted(missing_columns))

    exclusivity_column = get_exclusivity_column(data.columns)
    exact_matches, generic_matches, designation_matches = build_reference_indexes(
        load_reference(reference_file)
    )
    documents = defaultdict(dict)
    exact_count = 0
    generic_count = 0
    skipped_count = 0

    for _, row in data.iterrows():
        signature = record_signature(
            row["Generic Name"], row["Date Designated"], row["Orphan Designation"]
        )
        identities = list(exact_matches.get(signature, {}).values())
        exact = bool(identities)

        if exact:
            exact_count += 1
        else:
            identities = list(
                generic_matches.get(normalized_text(row["Generic Name"]), {}).values()
            )
            if identities:
                generic_count += 1
            else:
                skipped_count += 1
                continue

        designation_enrichments = list(
            designation_matches.get(
                normalized_text(row["Orphan Designation"]), {}
            ).values()
        )
        fallback_enrichment = (
            designation_enrichments[0] if len(designation_enrichments) == 1 else {}
        )

        for identity in identities:
            orphan_enrichment = identity.get("orphan_designation", fallback_enrichment)
            record = build_record(
                row,
                identity["identifiers"],
                orphan_enrichment,
                exclusivity_column,
            )
            record_key = json.dumps(record, sort_keys=True, ensure_ascii=False)
            documents[identity["_id"]][record_key] = record

    LOGGER.info(
        "FDA orphan-drug rows: %s exact reference matches, %s generic-name matches, "
        "%s skipped without a chemical identifier",
        exact_count,
        generic_count,
        skipped_count,
    )

    for document_id in sorted(documents):
        yield {
            "_id": document_id,
            "fda_orphan_drug": list(documents[document_id].values()),
        }
