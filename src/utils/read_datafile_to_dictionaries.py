"""Primary datafile reading functions.

Called by src/run.py to correctly parse primary input files.

Todo:
    * Add parser for accession list (.txt) files
    * Add parser for sacra output (.json) files
"""
from __future__ import division, print_function
import sys
import logging
logger = logging.getLogger(__name__)

def read_datafile_to_dictionaries(fname, CONFIG):
    """Return a (filetype, [list of dictionaries]).

    The filetype is inferred from the filename, and the list
    of dictionaries is then constructed based on the inferred
    filetype."""
    logger.info("Reading {} to dictionaries.".format(fname))

    ftype = infer_ftype(fname.lower())

    if ftype == "ACCESSIONS":
        data_dicts = []
    elif ftype == "FASTA":
        data_dicts = read_fasta_to_dicts(fname, CONFIG)
    elif ftype == "JSON":
        data_dicts = []
    else:
        logger.error("Unknown input filetype for {}. Fatal.".format(ftype)); sys.exit(2)

    return (ftype, data_dicts)

def infer_ftype(fname):
    """Determind filetypes by reading fname suffixes."""
    if fname.endswith(".fasta") or fname.endswith(".fa"):
        ftype = "FASTA"
    elif fname.endswith(".txt"):
        ftype = "ACCESSIONS"
    elif fname.endswith(".json"):
        ftype = "JSON"
    else:
        logger.error("Unknown file type for file: {}".format(fname))
    return ftype

def read_fasta_to_dicts(fname, CONFIG):
    """Construct a list of dictionaries from a FASTA file.

    We define a FASTA block as one line of metadata (denoted by a `>`)
    and its associated nucleotide sequence in the following line(s).

    Each {key (str): value (str)} dictionary represents one block of
    data from the FASTA file. The keys of each dictionary correspond
    to the FASTA header fields defined in the CONFIG file."""
    from Bio import SeqIO
    logger.info('Reading in FASTA from {}.'.format(fname))

    data_dicts = []
    with open(fname, "rU") as f:

        for record in SeqIO.parse(f, "fasta"):
            data = {}
            if record.description in CONFIG["fasta_header_swaps"]:
                record.description = CONFIG["fasta_header_swaps"][record.description]
            head = record.description.split(CONFIG['fasta_separator_character'])

            if len(head) != len(CONFIG["fasta_headers"]):
                logger.warn("Skipping {} which had {} fields (expected {})".format(record.description, len(head), len(CONFIG["fasta_headers"])))
                continue
            for i in range(len(CONFIG["fasta_headers"])):
                try:
                    data[CONFIG["fasta_headers"][i]] = head[i]
                    data['sequence'] = str(record.seq)
                except KeyError:
                    logger.critical("Error parsing FASTA header. Header: {}. CONFIG specifies: {}".format(head, CONFIG["fasta_headers"])); sys.exit(2)
            data_dicts.append(data)
    return data_dicts
