import csv
import os

import pandas as pd
from biothings import config

from .csvsort import csvsort

logging = config.logger

# Priority list for selecting the document _id
ID_PRIORITY_LIST = {
    "chebi": "CHEBI",
    "pubchem": "PUBCHEM.COMPOUND",
    "chembl": "CHEMBL.COMPOUND",
    "drugbank": "DRUGBANK",
    "drugcentral": "DrugCentral",
    "hmdb": "HMDB",
    "pharmgkb": "PharmGKB",
}


def load_annotations(data_folder, chunk_size=1_000_000):
    """
    Stream through UniChem legacy dumps and yield one dict per compound:
      - PubChem IDs are cast to int
      - _id is chosen by ID_PRIORITY_LIST (first match)
      - fallback _id is the InChIKey (also stored under unichem['inchikey'])
      - no final sort by InChIKey—grouping done on-the-fly by UCI
    """
    logging.info(f"Starting UniChem parser with data folder: {data_folder}")
    logging.info(f"Using chunk size: {chunk_size:,}")
    logging.info(f"ID priority list: {ID_PRIORITY_LIST}")

    # 1) build source_dict: { src_id (int) -> src_name (lowercase str) }
    logging.info("Step 1: Building source dictionary from UC_SOURCE.txt")
    src_path = os.path.join(data_folder, "UC_SOURCE.txt")
    df_src = pd.read_csv(
        src_path, sep="\t", header=None,
        usecols=[0, 1], names=["src_id", "src_name"],
        dtype={"src_id": "int8", "src_name": "str"},
    )
    source_dict = {int(r.src_id): r.src_name.lower()
                   for r in df_src.itertuples()}
    logging.info(f"Built source dictionary with {len(source_dict)} sources: "
                 f"{list(source_dict.values())}")

    # 2) dump-and-sort UC_STRUCTURE → structure_df.csv
    logging.info("Step 2: Processing UC_STRUCTURE.txt in chunks and "
                 "sorting by UCI")
    struct_in = os.path.join(data_folder, "UC_STRUCTURE.txt")
    struct_out = os.path.join(data_folder, "structure_df.csv")
    sdtype = {"uci": "int64", "standardinchikey": "str"}
    struct_reader = pd.read_csv(
        struct_in, sep="\t", header=None,
        names=["uci_old", "standardinchi", "standardinchikey", "created",
               "username", "fikhb", "uci", "parent_smiles"],
        usecols=["uci", "standardinchikey"],
        dtype=sdtype, chunksize=chunk_size,
    )
    first = True
    chunk_count = 0
    for chunk in struct_reader:
        chunk_count += 1
        if chunk_count % 10 == 0:
            logging.info(f"Processed {chunk_count} structure chunks "
                         f"({chunk_count * chunk_size:,} rows)")
        chunk = chunk[['uci', 'standardinchikey']]
        chunk.to_csv(struct_out, index=False,
                     mode="w" if first else "a",
                     header=first)
        first = False
    logging.info(f"Completed processing {chunk_count} structure chunks")
    logging.info("Sorting structure data by UCI...")
    csvsort(struct_out, [0], numeric_column=True)  # sort by UCI (col 0)
    logging.info("Structure data sorting completed")

    # 3) dump-and-sort UC_XREF → xref_df.csv
    logging.info("Step 3: Processing UC_XREF.txt in chunks and sorting by UCI")
    xref_in = os.path.join(data_folder, "UC_XREF.txt")
    xref_out = os.path.join(data_folder, "xref_df.csv")
    xdtype = {"src_id": "int8", "src_compound_id": "str", "uci": "int64"}
    xref_reader = pd.read_csv(
        xref_in, sep="\t", header=None,
        names=["uci_old", "src_id", "src_compound_id", "assignment",
               "last_release_u_when_current", "created", "lastupdated",
               "userstamp", "aux_src", "uci"],
        usecols=["src_id", "src_compound_id", "uci"],
        dtype=xdtype, chunksize=chunk_size,
    )
    first = True
    chunk_count = 0
    for chunk in xref_reader:
        chunk_count += 1
        if chunk_count % 10 == 0:
            logging.info(f"Processed {chunk_count} xref chunks "
                         f"({chunk_count * chunk_size:,} rows)")
        chunk.to_csv(xref_out, index=False,
                     mode="w" if first else "a",
                     header=first)
        first = False
    logging.info(f"Completed processing {chunk_count} xref chunks")
    logging.info("Sorting xref data by UCI...")
    csvsort(xref_out, [2], numeric_column=True)  # sort by UCI (col 2)
    logging.info("Xref data sorting completed")

    # 4) stream-merge & group by UCI → yield final docs
    logging.info("Step 4: Stream-merging structure and xref data by UCI")
    yield from _stream_merge_and_group(struct_out, xref_out, source_dict)


def _stream_merge_and_group(struct_csv, xref_csv, source_dict):
    """
    Merge two UCI-sorted CSVs row by row, accumulate all cross-refs
    for each UCI/InChIKey, then finalize each document.
    """
    logging.info("Starting stream merge and grouping process")
    documents_yielded = 0
    orphan_xrefs_skipped = 0

    with open(struct_csv, newline="") as sf, open(xref_csv, newline="") as xf:
        struct_reader = csv.DictReader(sf)
        xref_reader = csv.DictReader(xf)

        struct_row = next(struct_reader, None)
        xref_row = next(xref_reader,   None)

        current_uci = None
        current_inchikey = None
        entry = None

        while struct_row and xref_row:
            uci_s = int(struct_row["uci"])
            uci_x = int(xref_row["uci"])
            if uci_s < uci_x:
                struct_row = next(struct_reader, None)
            elif uci_s > uci_x:
                # orphan xref → skip
                orphan_xrefs_skipped += 1
                if orphan_xrefs_skipped % 100000 == 0:
                    logging.debug(f"Skipped {orphan_xrefs_skipped:,} "
                                  f"orphan xrefs")
                xref_row = next(xref_reader, None)
            else:
                # same UCI → process this cross-ref
                if current_uci != uci_x:
                    # finishing previous group?
                    if entry is not None:
                        documents_yielded += 1
                        if documents_yielded % 50000 == 0:
                            logging.info(f"Yielded {documents_yielded:,} "
                                         f"documents")
                        yield _finalize_entry(entry, current_inchikey)
                    # start new group
                    current_uci = uci_x
                    current_inchikey = struct_row["standardinchikey"]
                    entry = {"unichem": {}}

                # map source ID → name → value
                src_id = int(xref_row["src_id"])
                source = source_dict.get(src_id)
                if source:
                    cid = xref_row["src_compound_id"]
                    # format per source
                    if source == "chebi":
                        cid = f"CHEBI:{cid}"
                    elif source == "pubchem":
                        try:
                            cid = int(cid)
                        except ValueError:
                            pass
                    # accumulate into entry["unichem"]
                    existing = entry["unichem"].get(source)
                    if existing is None:
                        entry["unichem"][source] = cid
                    else:
                        if isinstance(existing, list):
                            existing.append(cid)
                        else:
                            entry["unichem"][source] = [existing, cid]

                # advance xref
                xref_row = next(xref_reader, None)

        # yield the very last group
        if entry is not None:
            documents_yielded += 1
            yield _finalize_entry(entry, current_inchikey)

        logging.info(f"Stream merge completed: yielded {documents_yielded:,} "
                     f"total documents, skipped {orphan_xrefs_skipped:,} "
                     f"orphan xrefs")


def _finalize_entry(entry, inchikey):
    """
    Choose the top-level _id by ID_PRIORITY_LIST (first match),
    always save inchikey under 'unichem'.
    """
    # always include the inchikey
    entry["unichem"]["inchikey"] = inchikey

    # pick primary _id
    chosen_id_source = None
    for key in ID_PRIORITY_LIST:
        if key in entry["unichem"]:
            val = entry["unichem"][key]
            # if list, take the first element
            if isinstance(val, list):
                val = val[0]

            # Apply prefix from ID_PRIORITY_LIST
            prefix = ID_PRIORITY_LIST[key]
            if prefix and not str(val).startswith(prefix):
                entry["_id"] = f"{prefix}:{val}"
            else:
                entry["_id"] = str(val) if isinstance(val, int) else val
            chosen_id_source = key
            break
    else:
        # fallback to the inchikey itself
        # entry["_id"] = inchikey
        entry["_id"] = f'INCHIKEY:{inchikey}'
        chosen_id_source = "inchikey"

    # Log ID selection for debugging (only occasionally to avoid spam)
    if chosen_id_source and hash(inchikey) % 10000 == 0:
        sources_found = list(entry["unichem"].keys())
        logging.debug(f"ID selection - Sources found: {sources_found}, "
                      f"Chosen: {chosen_id_source}, ID: {entry['_id']}")

    return entry
