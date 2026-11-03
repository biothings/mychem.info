# -*- coding: utf-8 -*-

import concurrent.futures, csv, heapq, logging, multiprocessing, os, sys, tempfile
if sys.version_info.major == 2:
    from io import open
from optparse import OptionParser
csv.field_size_limit(2**30) # can't use sys.maxsize because of Windows error


class CsvSortError(Exception):
    pass


def csvsort(input_filename,
            columns,
            output_filename=None,
            max_size=100,
            has_header=True,
            delimiter=',',
            show_progress=False,
            parallel=True,
            quoting=csv.QUOTE_MINIMAL,
            encoding=None,
            numeric_column=False):
    
    """Sort the CSV file on disk rather than in memory.

    The merge sort algorithm is used to break the file into smaller sub files

    Args:
        input_filename: the CSV filename to sort.
        columns: a list of columns to sort on (can be 0 based indices or header
            keys).
        output_filename: optional filename for sorted file. If not given then
            input file will be overriden.
        max_size: the maximum size (in MB) of CSV file to load in memory at
            once.
        has_header: whether the CSV contains a header to keep separated from
            sorting.
        delimiter: character used to separate fields, default ','.
        show_progress (Boolean): A flag whether or not to show progress.
            The default is False, which does not print any merge information.
        quoting: How much quoting is needed in the final CSV file.  Default is
            csv.QUOTE_MINIMAL.
        encoding: The name of the encoding to use when opening or writing the
            csv files. Default is None which uses the system default.
    """

    with open(input_filename, newline='', encoding=encoding) as input_fp:
        reader = csv.reader(input_fp, delimiter=delimiter)
        if has_header:
            header = next(reader)
        else:
            header = None

        columns = parse_columns(columns, header)

        filenames = csvsplit(reader, max_size)
        if show_progress:
            logging.info('Merging %d splits' % len(filenames))

        if parallel:
            concurrency = multiprocessing.cpu_count()
            map_args = [(filename, columns, numeric_column, encoding) for filename in filenames]
            if not getattr(sys, "_is_gil_enabled", lambda: True)():
                # free-threaded Python: threads sort in parallel, and forking
                # the (multi-threaded) hub process wouldn't be safe
                with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                    for future in [executor.submit(memorysort, *args) for args in map_args]:
                        future.result()
            else:
                # Python 3.14 defaults to "forkserver", which re-imports the hub in every worker
                with multiprocessing.get_context("fork").Pool(processes=concurrency) as pool:
                    pool.starmap(memorysort, map_args)
        else:
            for filename in filenames:
                memorysort(filename, columns, numeric_column, encoding)
        sorted_filename = mergesort(filenames, columns, numeric_column, encoding=encoding)

    # XXX make more efficient by passing quoting, delimiter, and moving result
    # generate the final output file
    with open(output_filename or input_filename, 'w', newline='', encoding=encoding) as output_fp:
        writer = csv.writer(output_fp, delimiter=delimiter, quoting=quoting)
        if header:
            writer.writerow(header)
        with open(sorted_filename, newline='', encoding=encoding) as sorted_fp:
            for row in csv.reader(sorted_fp):
                writer.writerow(row)

    os.remove(sorted_filename)


def parse_columns(columns, header):
    """check the provided column headers
    """
    for i, column in enumerate(columns):
        if isinstance(column, int):
            if header:
                if column >= len(header):
                    raise CsvSortError(
                        'Column index is out of range: "{}"'.format(column))
        else:
            # find index of column from header
            if header is None:
                raise CsvSortError(
                    'CSV needs a header to find index of this column name:' +
                    ' "{}"'.format(column))
            else:
                if column in header:
                    columns[i] = header.index(column)
                else:
                    raise CsvSortError(
                        'Column name is not in header: "{}"'.format(column))
    return columns


def csvsplit(reader, max_size):
    """Split into smaller CSV files of maximum size and return the filenames.
    """
    max_size = max_size * 1024 * 1024  # convert to bytes
    writer = None
    current_size = 0
    split_filenames = []

    # break CSV file into smaller merge files
    for row in reader:
        if writer is None:
            ntf = tempfile.NamedTemporaryFile(delete=False, mode='w')
            writer = csv.writer(ntf)
            split_filenames.append(ntf.name)

        writer.writerow(row)
        current_size += sys.getsizeof(row)
        if current_size > max_size:
            writer = None
            current_size = 0
    return split_filenames


def memorysort(filename, columns, numeric_column, encoding=None):
    """Sort this CSV file in memory on the given columns
    """
    with open(filename, newline='', encoding=encoding) as input_fp:
        rows = [row for row in csv.reader(input_fp) if row]

    rows.sort(key=lambda row: get_key(row, columns, numeric_column))
    with open(filename, 'w', newline='', encoding=encoding) as output_fp:
        writer = csv.writer(output_fp)
        for row in rows:
            writer.writerow(row)


def get_key(row, columns, numeric_column):
    """Get sort key for this row
    """
    if(numeric_column):
        return [int(row[column]) for column in columns]
    else:
        return [row[column] for column in columns]

def decorated_csv(filename, columns, numeric_column, encoding=None):
    """Iterator to sort CSV rows
    """
    with open(filename, newline='', encoding=encoding) as fp:
        for row in csv.reader(fp):
            yield get_key(row, columns, numeric_column), row


def mergesort(sorted_filenames, columns, numeric_column, nway=2, encoding=None):
    """Merge these 2 sorted csv files into a single output file
    """
    merge_n = 0
    while len(sorted_filenames) > 1:
        merge_filenames, sorted_filenames = \
           sorted_filenames[:nway], sorted_filenames[nway:]

        with tempfile.NamedTemporaryFile(delete=False, mode='w') as output_fp:
            writer = csv.writer(output_fp)
            merge_n += 1
            for _, row in heapq.merge(*[decorated_csv(filename, columns, numeric_column, encoding)
                                        for filename in merge_filenames]):
                writer.writerow(row)

            sorted_filenames.append(output_fp.name)

        for filename in merge_filenames:
            os.remove(filename)
    return sorted_filenames[0]


def main():
    parser = OptionParser()
    parser.add_option(
        '-c',
        '--column',
        dest='columns',
        action='append',
        help='column of CSV to sort on')
    parser.add_option(
        '-s',
        '--size',
        dest='max_size',
        type='float',
        default=100,
        help='maximum size of each split CSV file in MB (default 100)')
    parser.add_option(
        '-n',
        '--no-header',
        dest='has_header',
        action='store_false',
        default=True,
        help='set CSV file has no header')
    parser.add_option(
        '-d',
        '--delimiter',
        default=',',
        help='set CSV delimiter (default ",")')
    parser.add_option(
        '-e',
        '--encoding',
        default=None,
        help='character encoding (eg utf-8) to use when reading/writing files (default uses system default)')
    args, input_files = parser.parse_args()

    if not input_files:
        parser.error('What CSV file should be sorted?')
    elif not args.columns:
        parser.error('Which columns should be sorted on?')
    else:
        # escape backslashes
        args.delimiter = args.delimiter.decode('string_escape')
        args.columns = [int(column) if column.isdigit() else column
                        for column in args.columns]
        csvsort(
            input_files[0],
            columns=args.columns,
            max_size=args.max_size,
            has_header=args.has_header,
            delimiter=args.delimiter,
            encoding=args.encoding)


if __name__ == '__main__':
    main()
