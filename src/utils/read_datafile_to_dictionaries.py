from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)

def read_datafile_to_dictionaries(fname):
    """ returns a [filetype, [list of dictionaries]] """
    logger.info("Reading" + fname)

    dummy_dict = {
        'strain_id': 'strain_name_1',
        'strain_name': 'strain_name_1',
        'sample_id': 'sample_name_1',
        'sample_name': 'sample_name_1',
        'accession': 'ACC',
        'sequence': 'ATCG',
        'attribution_id': 'attribution_id_1'
    }
    return ("JSON", [dummy_dict])
