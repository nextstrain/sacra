from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)

def read_metafile_to_dictionaries(fname):
    """ returns a (tag, [list of dictionaries]) """
    logger.info("Reading metadata file: {}".format(fname))

    ftype = determine_metadata_file_type(fname)
    if ftype == 'tsv':
        tag, meta_dictionaries = parse_metadata_tsv(fname)
    else:
        logger.error("Couldn't parse metadata file.")
        tag, meta_dictionaries = None, []
    return (tag, meta_dictionaries)

def determine_metadata_file_type(fname):
    """Parse a metadata file suffix to determine its file type.

    Files are assumed to be tsv if they end in .tsv or .txt
    Files are assumed to be csv if they end in .csv
    Files are assumed to be excel spreadsheets if they end in .xls or .xlsx

    If no valid file type can be determined, returns "unknown".
    """
    fname = fname.lower()
    if fname.endswith('.tsv') or fname.endswith('.txt'):
        ftype = 'tsv'
    elif fname.endswith('.csv'):
        ftype = 'csv'
    elif fname.endswith('.xls') or fname.endswith('.xlsx'):
        ftype = 'excel'
    else:
        ftype = 'unknown'
    return ftype

def parse_metadata_tsv(fname):
    """Create a set of dictionaries out of a metadata tsv with a header."""
    sep = '\t'
    with open(fname, 'r') as f:
        header = f.readline().split(sep)
        tag = header[0]
        dicts = []

        for line in f.readlines():
            line = line.split(sep)
            try:
                assert len(line) == len(header), "Metadata TSV line length mismatched from header."
                dicts.append({ k: v for (k,v) in zip(header, line) })
            except:
                logger.error("Couldn't read line in metadata TSV.")

    return (tag, dicts)
