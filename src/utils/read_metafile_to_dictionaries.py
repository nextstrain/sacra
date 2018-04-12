from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)

def read_metafile_to_dictionaries(fname):
    """ returns a (tag, [list of dictionaries]) """
    logger.info("Reading meta" + fname)

    dummy_dict = {
        'accession': 'ACC',
        'country': 'England',
    }
    return ("accession", [dummy_dict])
