import pandas as pd
import os, csv, re
import numpy as np
from biothings.utils.dataload import dict_convert, dict_sweep
from .csvsort import csvsort
from biothings import config
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
    current_chunk_size = 1000000;
    # load source files
    source_file = os.path.join(data_folder,"UC_SOURCE.txt")
    struct_file = os.path.join(data_folder,"UC_STRUCTURE.txt")
    xref_file = os.path.join(data_folder,"UC_XREF.txt")
    assert os.path.exists(source_file)
    assert os.path.exists(struct_file)
    assert os.path.exists(xref_file)

    # create source dictionary, {source id: name of source}
    source_tsv = pd.read_csv(source_file, sep='\t', header= None)
    source_keys = list(source_tsv[0])
    source_values = list(source_tsv[1])
    source_dict = {source_keys[i]: source_values[i] for i in range(len(source_keys))}


    ## make structure file (condensed, then sorted) by reading and appending new file in chunks - too big to load all at once
    sdtype={'uci':'int64','standardinchikey':'str'}

    structure_df_chunk = pd.read_csv(struct_file, sep='\t', header=None, usecols=['uci', 'standardinchikey'],
                                         names=['uci_old','standardinchi','standardinchikey','created','username','fikhb','uci','parent_smiles'],
                                         chunksize=current_chunk_size, dtype=sdtype)


    smerge_counter = 0; # use merge counter to append file after file is created
    for chunk in structure_df_chunk:
        if(smerge_counter == 0):
            chunk.to_csv(path_or_buf=os.path.join(data_folder,"structure_df.csv"), index=False)
            smerge_counter = 1;
        else:
            chunk.to_csv(path_or_buf=os.path.join(data_folder,"structure_df.csv"), index=False, mode='a', header=False)

    del structure_df_chunk # clear from memory

    ## use customized csvsort function - from edited csvsort module - see csvsort folder - sort by uci (column index 1)
    csvsort(os.path.join(data_folder,"structure_df.csv"),[1],numeric_column=True)


    ## make xref file - condensed
    xdtype={'src_id':'int8','src_compound_id':'str','uci':'int64'}

    xref_df_chunk = pd.read_csv(xref_file, sep='\t', header=None, usecols=['src_id','src_compound_id', 'uci'],
                                         names=['uci_old','src_id','src_compound_id','assignment','last_release_u_when_current','created ','lastupdated','userstamp','aux_src','uci'],
                                         chunksize=current_chunk_size, dtype=xdtype)

    xmerge_counter = 0;

    for chunk in xref_df_chunk:
        if(xmerge_counter == 0):
            chunk.to_csv(path_or_buf=os.path.join(data_folder,"xref_df.csv"), index=False)
            xmerge_counter = 1;
        else:
            chunk.to_csv(path_or_buf=os.path.join(data_folder,"xref_df.csv"), index=False, mode='a', header=False)

    del xref_df_chunk

    ## use customized csvsort function to sort xref file by uci (column index 2)
    csvsort(os.path.join(data_folder,"xref_df.csv"),[2],numeric_column=True)


    ## make data frame that keeps track of min and max uci value for each structure chunk
    chunk_counter = 0
    structure_df_chunk = pd.read_csv(os.path.join(data_folder, "structure_df.csv"), chunksize=current_chunk_size)
    min_max_columns = ["chunk_start", "min_uci", "max_uci"]
    min_max_dfs = []  # Initialize an empty list to hold DataFrame chunks    for schunk in structure_df_chunk:
    for schunk in structure_df_chunk:
        chunk_start = chunk_counter * current_chunk_size
        chunk_min = schunk["uci"].min()
        chunk_max = schunk["uci"].max()
        chunk_counter = 1
        min_max_dfs.append(pd.DataFrame([[chunk_start, chunk_min, chunk_max]], columns=min_max_columns))

    structure_min_max_df = pd.concat(min_max_dfs, ignore_index=True)  # Use concat to combine the chunks

    xdf_chunk = pd.read_csv(os.path.join(data_folder,"xref_df.csv"), chunksize=current_chunk_size)

    ## loop through xdf chunks. merge with all structure chunks that have overlapping uci values
    merge_counter = 0;
    for xchunk in xdf_chunk:
        current_x_min = min(xchunk["uci"])
        current_x_max = max(xchunk["uci"])
        for index, row in structure_min_max_df.iterrows():
            if(not((current_x_max < row['min_uci']) or (current_x_min > row['max_uci']))):
                sdf_chunk = pd.read_csv(os.path.join(data_folder,"structure_df.csv"), skiprows = row["chunk_start"], header=0, names=['standardinchikey','uci'], nrows=current_chunk_size)
                complete_df_chunk = pd.merge(left=sdf_chunk, right=xchunk, left_on='uci', right_on='uci')
                if(merge_counter == 0):
                    complete_df_chunk.to_csv(path_or_buf=os.path.join(data_folder,"complete_df.csv"), index=False)
                    merge_counter = 1;
                else:
                    complete_df_chunk.to_csv(path_or_buf=os.path.join(data_folder,"complete_df.csv"), index=False, mode='a', header=False)


    del sdf_chunk
    del xdf_chunk

    ## sort complete_df (merged structure and xref file) based on inchikey - alphabetically
    csvsort(os.path.join(data_folder,"complete_df.csv"),[0], numeric_column = False)



    ## loop through merged complete data frame in chunks
    complete_df_chunk = pd.read_csv(os.path.join(data_folder,"complete_df.csv"), chunksize=current_chunk_size)


    new_entry = {} ## each entry will be made based on inchikey
    last_inchi = ''; ## keep track of the inchikey from the previous row looked at in the complete dataframe

    for chunk in complete_df_chunk:
        for row in chunk.itertuples():
            inchi = row[1]
            source = source_dict[row[3]]
            source_id = row[4]
            # make sure there are no missing values in entry (would show as nan)
            if((source_id == source_id) and (source == source) and (inchi == inchi)):
                # reformat chebi source id to fit MyChem.info syntax
                if(source == 'chebi'):
                    source_id = 'CHEBI:' + source_id
                # check to see if previous entry had same inchi code. if so,
                if(last_inchi == inchi):
                    # if source id already exists for source, then create/add to list. if not, create first entry for source
                    if(source in new_entry["unichem"]):
                        if(type(new_entry["unichem"][source]) == str):
                            new_entry["unichem"][source] = [new_entry["unichem"][source], source_id]
                        else:
                            new_entry["unichem"][source].append(source_id)
                    else:
                        new_entry["unichem"][source] = source_id
                elif(len(last_inchi) == 0):
                    new_entry = {
                        "_id" : inchi,
                        "unichem": {
                            source: source_id
                        }
                    }
                    last_inchi = inchi
                else:
                    yield new_entry; ## yield created entry from previous row(s) when inchikey changes
                    new_entry = {
                        "_id" : inchi,
                        "unichem": {
                            source: source_id
                        }
                    }
                last_inchi = inchi ## set last_inchi to the inchikey used in current iteration

    yield new_entry ## submit final entry
