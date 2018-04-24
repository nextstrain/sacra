from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)

def read_datafile_to_dictionaries(fname, CONFIG):
    """ returns a [filetype, [list of dictionaries]] """
    logger.info("Reading {} to dictionaries.".format(fname))

    ftype = infer_ftype(fname)

    if ftype == "ACCESSIONS":
        data_dicts = []
    elif ftype == "FASTA":
        data_dicts = read_fasta_to_dicts(fname, CONFIG)
    elif ftype == "JSON":
        data_dicts = []
    else:
        logger.error("Unknown input filetype for {}. Fatal.".format(f)); sys.exit(2)

    return (ftype, data_dicts)

def infer_ftype(fname):
    if fname.endswith(".fasta"):
        return "FASTA"
    if fname.endswith(".txt"):
        return "ACCESSIONS"
    elif (fname.endswith(".json")):
        return "JSON"

def read_fasta_to_dicts(fname, CONFIG):
    from Bio import SeqIO
    '''
    Take a fasta file and a list of information contained in its headers
    and build a dataset object from it.

    # TODO: This should return a docs structure
    # (list of docs dicts) instead of its current behavior
    '''
    logger.info('Reading in FASTA from %s.' % (fname))

    data_dicts = []
    # Read the fasta
    with open(fname, "rU") as f:

        for record in SeqIO.parse(f, "fasta"):
            data = {}
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
