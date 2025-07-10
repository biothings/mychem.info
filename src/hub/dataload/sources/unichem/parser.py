import csv
import os
import re

import numpy as np
import pandas as pd
from biothings import config
from biothings.utils.dataload import dict_convert, dict_sweep

from .csvsort import csvsort

logging = config.logger


def load_annotations(data_folder):
    """Load annotations function

    1. Create source dictionary for source name for source id (src_id)

    2. Sort structure and xref files by uci (csvsort)

    3. Merge structure and xref files by uci, keeping only uci, standardinchikey,
    src_id, and src_compound_id.

    4. Sort by standardinchikey so all entries next to each other (csvsort)

    5. Use source file to convert src_id to source name.

    6. Yeild document dictionaries one at a time (based on standardinchikey)
    """

    # change chunk size based on files. usually use 1M for full UniChem data files
    current_chunk_size = 1000000
    # load source files
    source_file = os.path.join(data_folder, "UC_SOURCE.txt")
    struct_file = os.path.join(data_folder, "UC_STRUCTURE.txt")
    xref_file = os.path.join(data_folder, "UC_XREF.txt")
    assert os.path.exists(source_file)
    assert os.path.exists(struct_file)
    assert os.path.exists(xref_file)

    logging.info("Starting UniChem data processing...")

    # Get file sizes for progress tracking
    struct_file_size = os.path.getsize(struct_file)
    xref_file_size = os.path.getsize(xref_file)
    logging.info(f"Structure file size: {struct_file_size / (1024**2):.1f} MB")
    logging.info(f"Xref file size: {xref_file_size / (1024**2):.1f} MB")

    # create source dictionary, {source id: name of source}
    source_tsv = pd.read_csv(source_file, sep='\t', header=None)
    source_keys = list(source_tsv[0])
    source_values = list(source_tsv[1])
    source_dict = {source_keys[i]: source_values[i]
                   for i in range(len(source_keys))}

    # make structure file (condensed, then sorted) by reading and appending new file in chunks - too big to load all at once
    logging.info("Step 1/6: Processing structure file...")
    sdtype = {'uci': 'int64', 'standardinchikey': 'str'}

    structure_df_chunk = pd.read_csv(struct_file, sep='\t', header=None, usecols=['uci', 'standardinchikey'],
                                     names=['uci_old', 'standardinchi', 'standardinchikey',
                                            'created', 'username', 'fikhb', 'uci', 'parent_smiles'],
                                     chunksize=current_chunk_size, dtype=sdtype)

    smerge_counter = 0  # use merge counter to append file after file is created
    bytes_processed = 0
    for chunk in structure_df_chunk:
        if (smerge_counter == 0):
            chunk.to_csv(path_or_buf=os.path.join(
                data_folder, "structure_df.csv"), index=False)
            smerge_counter = 1
        else:
            chunk.to_csv(path_or_buf=os.path.join(
                data_folder, "structure_df.csv"), index=False, mode='a', header=False)

        # Estimate bytes processed (rough approximation)
        bytes_processed += len(chunk) * 50  # Rough estimate per row
        progress = min(100, (bytes_processed / struct_file_size) * 100)
        if smerge_counter % 5 == 0:  # Log every 5th chunk to avoid spam
            logging.info(
                f"Structure file processing: {progress:.1f}% complete")

    del structure_df_chunk  # clear from memory
    logging.info("Step 1/6: Structure file processing completed")

    # use customized csvsort function - from edited csvsort module - see csvsort folder - sort by uci (column index 1)
    logging.info("Step 2/6: Sorting structure file by UCI...")
    csvsort(os.path.join(data_folder, "structure_df.csv"),
            [1], numeric_column=True)
    logging.info("Step 2/6: Structure file sorting completed")

    # make xref file - condensed
    logging.info("Step 3/6: Processing xref file...")
    xdtype = {'src_id': 'int8', 'src_compound_id': 'str', 'uci': 'int64'}

    xref_df_chunk = pd.read_csv(xref_file, sep='\t', header=None, usecols=['src_id', 'src_compound_id', 'uci'],
                                names=['uci_old', 'src_id', 'src_compound_id', 'assignment',
                                       'last_release_u_when_current', 'created ', 'lastupdated', 'userstamp', 'aux_src', 'uci'],
                                chunksize=current_chunk_size, dtype=xdtype)

    xmerge_counter = 0
    xbytes_processed = 0

    for chunk in xref_df_chunk:
        if (xmerge_counter == 0):
            chunk.to_csv(path_or_buf=os.path.join(
                data_folder, "xref_df.csv"), index=False)
            xmerge_counter = 1
        else:
            chunk.to_csv(path_or_buf=os.path.join(
                data_folder, "xref_df.csv"), index=False, mode='a', header=False)

        # Estimate bytes processed for xref file
        xbytes_processed += len(chunk) * 30  # Rough estimate per row
        progress = min(100, (xbytes_processed / xref_file_size) * 100)
        if xmerge_counter % 5 == 0:  # Log every 5th chunk to avoid spam
            logging.info(f"Xref file processing: {progress:.1f}% complete")

    del xref_df_chunk
    logging.info("Step 3/6: Xref file processing completed")

    # use customized csvsort function to sort xref file by uci (column index 2)
    logging.info("Step 4/6: Sorting xref file by UCI...")
    csvsort(os.path.join(data_folder, "xref_df.csv"), [2], numeric_column=True)
    logging.info("Step 4/6: Xref file sorting completed")

    # make data frame that keeps track of min and max uci value for each structure chunk
    chunk_counter = 0
    structure_df_chunk = pd.read_csv(os.path.join(
        data_folder, "structure_df.csv"), chunksize=current_chunk_size)
    min_max_columns = ["chunk_start", "min_uci", "max_uci"]
    # Initialize an empty list to hold DataFrame chunks    for schunk in structure_df_chunk:
    min_max_dfs = []
    for schunk in structure_df_chunk:
        chunk_start = chunk_counter * current_chunk_size
        chunk_min = schunk["uci"].min()
        chunk_max = schunk["uci"].max()
        chunk_counter += 1
        min_max_dfs.append(pd.DataFrame(
            [[chunk_start, chunk_min, chunk_max]], columns=min_max_columns))

    # Use concat to combine the chunks
    structure_min_max_df = pd.concat(min_max_dfs, ignore_index=True)

    xdf_chunk = pd.read_csv(os.path.join(
        data_folder, "xref_df.csv"), chunksize=current_chunk_size)

    # loop through xdf chunks. merge with all structure chunks that have overlapping uci values
    logging.info("Step 5/6: Merging structure and xref files...")
    merge_counter = 0
    xchunk_counter = 0
    for xchunk in xdf_chunk:
        xchunk_counter += 1
        current_x_min = min(xchunk["uci"])
        current_x_max = max(xchunk["uci"])
        for index, row in structure_min_max_df.iterrows():
            if (not ((current_x_max < row['min_uci']) or (current_x_min > row['max_uci']))):
                sdf_chunk = pd.read_csv(os.path.join(data_folder, "structure_df.csv"), skiprows=row["chunk_start"], header=0, names=[
                                        'standardinchikey', 'uci'], nrows=current_chunk_size)
                complete_df_chunk = pd.merge(
                    left=sdf_chunk, right=xchunk, left_on='uci', right_on='uci')
                if (merge_counter == 0):
                    complete_df_chunk.to_csv(path_or_buf=os.path.join(
                        data_folder, "complete_df.csv"), index=False)
                    merge_counter = 1
                else:
                    complete_df_chunk.to_csv(path_or_buf=os.path.join(
                        data_folder, "complete_df.csv"), index=False, mode='a', header=False)

        if xchunk_counter % 10 == 0:  # Log every 10th chunk to avoid spam
            logging.info(f"Processed {xchunk_counter} xref chunks for merging")

    del sdf_chunk
    del xdf_chunk
    logging.info("Step 5/6: Merging completed")

    # sort complete_df (merged structure and xref file) based on inchikey - alphabetically
    logging.info("Sorting merged data by InChI key...")
    csvsort(os.path.join(data_folder, "complete_df.csv"),
            [0], numeric_column=False)

    # loop through merged complete data frame in chunks
    logging.info("Step 6/6: Generating final documents...")
    complete_df_chunk = pd.read_csv(os.path.join(
        data_folder, "complete_df.csv"), chunksize=current_chunk_size)

    new_entry = {}  # each entry will be made based on inchikey
    last_inchi = ''  # keep track of the inchikey from the previous row looked at in the complete dataframe

    processed_rows = 0
    chunk_counter = 0

    for chunk in complete_df_chunk:
        chunk_counter += 1
        for row in chunk.itertuples():
            processed_rows += 1
            inchi = row[1]
            source = source_dict[row[3]]
            source_id = row[4]
            # make sure there are no missing values in entry (would show as nan)
            if ((source_id == source_id) and (source == source) and (inchi == inchi)):
                # reformat chebi source id to fit MyChem.info syntax
                if (source == 'chebi'):
                    source_id = 'CHEBI:' + source_id
                # convert pubchem source id to integer
                elif (source == 'pubchem'):
                    source_id = int(source_id)
                # check to see if previous entry had same inchi code. if so,
                if (last_inchi == inchi):
                    # if source id already exists for source, then create/add to list. if not, create first entry for source
                    if (source in new_entry["unichem"]):
                        if (type(new_entry["unichem"][source]) == list):
                            new_entry["unichem"][source].append(source_id)
                        else:
                            # Convert single value to list and add new value
                            new_entry["unichem"][source] = [
                                new_entry["unichem"][source], source_id]
                    else:
                        new_entry["unichem"][source] = source_id
                elif (len(last_inchi) == 0):
                    new_entry = {
                        "_id": inchi,
                        "unichem": {
                            source: source_id
                        }
                    }
                    last_inchi = inchi
                else:
                    # yield created entry from previous row(s) when inchikey changes
                    yield new_entry
                    new_entry = {
                        "_id": inchi,
                        "unichem": {
                            source: source_id
                        }
                    }
                last_inchi = inchi  # set last_inchi to the inchikey used in current iteration

        # Log progress every 10 chunks
        if chunk_counter % 10 == 0:
            logging.info(
                f"Processed {chunk_counter} chunks, {processed_rows:,} rows total")

    logging.info(
        f"Step 6/6: Document generation completed. Total rows processed: {processed_rows:,}")
    yield new_entry  # submit final entry
