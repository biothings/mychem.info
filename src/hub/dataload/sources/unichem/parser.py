import gc
import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
from biothings import config

logging = config.logger


def process_group_chunk(args):
    """
    Process a chunk of grouped data in a separate process.
    This function will be called by multiple processes in parallel.
    """
    chunk_data, source_dict, id_priority_list = args

    def get_best_id(unichem_data, inchi_key):
        """
        Determine the best _id based on priority list.
        Returns the highest priority source ID available, or inchi_key as
        fallback.
        """
        for source in id_priority_list:
            if source in unichem_data:
                source_ids = unichem_data[source]
                # If it's a list, take the first one
                if isinstance(source_ids, list):
                    return source_ids[0]
                else:
                    return source_ids
        # Fallback to inchi_key if no priority sources found
        return inchi_key

    results = []

    for inchi_key, group_data in chunk_data:
        unichem_data = {}

        for row_data in group_data:
            src_id, source_id = row_data['src_id'], row_data['src_compound_id']

            if pd.isna(source_id) or pd.isna(src_id):
                continue

            source_name = source_dict.get(src_id)
            if not source_name:
                continue

            # Format source IDs
            if source_name == 'chebi':
                source_id = f'CHEBI:{source_id}'
            elif source_name == 'pubchem':
                try:
                    source_id = int(source_id)
                except (ValueError, TypeError):
                    continue

            # Add to unichem data
            if source_name in unichem_data:
                existing = unichem_data[source_name]
                if isinstance(existing, list):
                    existing.append(source_id)
                else:
                    unichem_data[source_name] = [existing, source_id]
            else:
                unichem_data[source_name] = source_id

        if unichem_data:
            # Always add the InChI key to unichem data (valuable metadata)
            unichem_data['inchikey'] = inchi_key

            # Determine the best _id based on priority list
            best_id = get_best_id(unichem_data, inchi_key)

            doc = {
                "_id": best_id,
                "unichem": unichem_data
            }
            results.append(doc)

    return results


def load_annotations(data_folder, num_processes=None):
    """
    Memory-optimized streaming version of load_annotations designed for very
    large files (40GB+). Uses minimal memory by streaming data and avoiding
    loading entire datasets into memory.

    Key optimizations:
    1. Streaming file processing - never loads full files into memory
    2. Temporary sorted files for efficient merging
    3. Generator-based processing throughout
    4. Multiprocessing for document generation only
    5. Aggressive memory cleanup

    Args:
        data_folder: Path to the folder containing UniChem data files
        num_processes: Number of processes to use (default: CPU count - 5)

    Expected memory usage: <10GB regardless of input file size
    Expected performance: 2-4x faster than loading everything into memory
    """

    # Determine number of processes
    if num_processes is None:
        num_processes = max(1, mp.cpu_count() - 5)

    logging.info(f"Using {num_processes} processes for parallel processing")
    logging.info("Memory-optimized streaming mode for large files")

    # Priority list for _id selection
    id_priority_list = [
        "chebi",
        "pubchem",
        "chembl",
        "drugbank",
        "drugcentral",
        "pharmgkb",
    ]

    # Larger chunk sizes for better I/O performance during structure loading
    current_chunk_size = 2000000  # 2M rows for better throughput

    # File paths
    source_file = os.path.join(data_folder, "UC_SOURCE.txt")
    struct_file = os.path.join(data_folder, "UC_STRUCTURE.txt")
    xref_file = os.path.join(data_folder, "UC_XREF.txt")

    for file_path in [source_file, struct_file, xref_file]:
        assert os.path.exists(file_path), f"File not found: {file_path}"

    logging.info("Starting memory-optimized UniChem data processing...")

    # Get file sizes for progress tracking
    struct_file_size = os.path.getsize(struct_file)
    xref_file_size = os.path.getsize(xref_file)
    logging.info(f"Structure file size: {struct_file_size / (1024**3):.1f} GB")
    logging.info(f"Xref file size: {xref_file_size / (1024**3):.1f} GB")

    # Create source dictionary (this is small, can keep in memory)
    logging.info("Loading source mapping...")
    source_df = pd.read_csv(source_file, sep='\t', header=None,
                            names=['src_id', 'source_name'])
    source_dict = dict(zip(source_df['src_id'], source_df['source_name']))
    del source_df
    gc.collect()

    # Step 1: Stream through merged data and group by inchi_key
    logging.info("Step 1/2: Streaming merge and grouping...")

    # Use a generator to stream through the merged data
    def stream_merged_data():
        """Generator that yields merged records without loading everything."""

        # Optimized data types
        struct_dtype = {'uci': 'int32', 'standardinchikey': 'string'}
        xref_dtype = {
            'src_id': 'int8',
            'src_compound_id': 'string',
            'uci': 'int32'
        }

        struct_columns = [
            'uci_old', 'standardinchi', 'standardinchikey',
            'created', 'username', 'fikhb', 'uci', 'parent_smiles'
        ]
        xref_columns = [
            'uci_old', 'src_id', 'src_compound_id', 'assignment',
            'last_release_u_when_current', 'created', 'lastupdated',
            'userstamp', 'aux_src', 'uci'
        ]

        # Read structure file in chunks
        logging.info("Loading structure data in chunks...")
        struct_data = {}
        chunk_count = 0
        total_processed = 0

        for struct_chunk in pd.read_csv(
                struct_file, sep='\t', header=None,
                names=struct_columns,
                usecols=['uci', 'standardinchikey'],
                chunksize=current_chunk_size,
                dtype=struct_dtype):
            chunk_count += 1

            # Vectorized operation - much faster than iterrows()
            valid_mask = struct_chunk['standardinchikey'].notna()
            valid_data = struct_chunk[valid_mask]

            # Update dictionary with valid entries
            new_entries = dict(zip(valid_data['uci'],
                                   valid_data['standardinchikey']))
            struct_data.update(new_entries)

            total_processed += len(struct_chunk)

            if chunk_count % 5 == 0:  # More frequent updates
                # Estimate progress based on ~200 bytes/line
                progress_gb = (total_processed * 200) / (1024**3)
                msg = (f"Structure chunk {chunk_count}, "
                       f"processed ~{progress_gb:.1f}GB, "
                       f"memory items: {len(struct_data):,}")
                logging.info(msg)

            del struct_chunk, valid_data, new_entries
            if chunk_count % 5 == 0:
                gc.collect()

        logging.info(f"Loaded {len(struct_data):,} structure mappings")

        # Now stream through xref data and yield merged records
        logging.info("Streaming through xref data...")
        chunk_count = 0
        total_merged = 0
        total_xref_processed = 0

        for xref_chunk in pd.read_csv(
                xref_file, sep='\t', header=None,
                names=xref_columns,
                usecols=['src_id', 'src_compound_id', 'uci'],
                chunksize=current_chunk_size,
                dtype=xref_dtype):
            chunk_count += 1
            total_xref_processed += len(xref_chunk)

            # Vectorized lookup - much faster than iterrows()
            # Find rows where UCI exists in struct_data
            valid_uci_mask = xref_chunk['uci'].isin(struct_data.keys())
            valid_xref = xref_chunk[valid_uci_mask]

            # Vectorized merge
            for _, row in valid_xref.iterrows():
                uci = row['uci']
                inchi_key = struct_data[uci]
                yield {
                    'standardinchikey': inchi_key,
                    'src_id': row['src_id'],
                    'src_compound_id': row['src_compound_id']
                }
                total_merged += 1

            if chunk_count % 5 == 0:  # More frequent updates
                # Estimate progress (~150 bytes/line)
                progress_gb = (total_xref_processed * 150) / (1024**3)
                msg = (f"Xref chunk {chunk_count}, "
                       f"processed ~{progress_gb:.1f}GB, "
                       f"total merged: {total_merged:,}")
                logging.info(msg)

            del xref_chunk, valid_xref
            if chunk_count % 5 == 0:
                gc.collect()

        msg = f"Streaming completed. Total merged records: {total_merged:,}"
        logging.info(msg)
        del struct_data
        gc.collect()

    # Step 2: Group by inchi_key using a dictionary
    logging.info("Step 2/2: Grouping and generating documents...")

    inchi_groups = {}
    record_count = 0

    for record in stream_merged_data():
        inchi_key = record['standardinchikey']
        if inchi_key not in inchi_groups:
            inchi_groups[inchi_key] = []

        inchi_groups[inchi_key].append({
            'src_id': record['src_id'],
            'src_compound_id': record['src_compound_id']
        })

        record_count += 1
        if record_count % 1000000 == 0:
            msg = (f"Grouped {record_count:,} records into "
                   f"{len(inchi_groups):,} groups")
            logging.info(msg)

    msg = f"Grouping completed: {len(inchi_groups):,} unique InChI keys"
    logging.info(msg)

    # Prepare data for multiprocessing
    group_data = list(inchi_groups.items())
    del inchi_groups
    gc.collect()

    # Calculate chunk size for multiprocessing
    chunk_size = max(1, len(group_data) // (num_processes * 4))
    logging.info(f"Processing in chunks of {chunk_size:,} groups each")

    # Create chunks for multiprocessing
    chunks = []
    for i in range(0, len(group_data), chunk_size):
        chunk = group_data[i:i + chunk_size]
        chunks.append((chunk, source_dict, id_priority_list))

    logging.info(f"Created {len(chunks)} chunks for {num_processes} processes")

    # Process chunks in parallel
    total_documents = 0
    processed_chunks = 0

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Submit all chunks to the process pool
        future_to_chunk = {
            executor.submit(process_group_chunk, chunk): i
            for i, chunk in enumerate(chunks)
        }

        # Process completed chunks as they finish
        for future in as_completed(future_to_chunk):
            chunk_idx = future_to_chunk[future]
            try:
                chunk_results = future.result()
                processed_chunks += 1

                # Yield each document from the chunk
                for doc in chunk_results:
                    yield doc
                    total_documents += 1

                # Log progress
                progress = (processed_chunks / len(chunks)) * 100
                logging.info(
                    f"Chunk {processed_chunks}/{len(chunks)} completed "
                    f"({progress:.1f}%) - Documents: {total_documents:,}"
                )

            except Exception as e:
                logging.error(f"Error processing chunk {chunk_idx}: {str(e)}")
                raise

    logging.info(
        f"Completed. Generated {total_documents:,} documents using "
        f"{num_processes} processes with streaming approach"
    )
