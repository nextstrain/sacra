from file_readers import parse_geo_synonyms, make_dict_from_file
import logging
logger = logging.getLogger(__name__)

"""
Given the lookups (name -> filename) defined in the config
parse the files and replace the filename (in config) with the
parsed lookup
"""


def populate_lookups(config):
    for key, fname in config["lookups"].iteritems():
        # try:
        tmp = make_dict_from_file(fname)
        config["lookups"][key] = tmp
        # except:
        #     logger.error("Couldn't load lookup file", fname)
        #     import pdb; pdb.set_trace()
        #     config["lookups"][key] = None
