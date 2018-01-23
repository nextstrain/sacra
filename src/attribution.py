from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.append('')
from spec_mapping import mapping as sm


class Attribution:

    def __init__(self, data_dictionary):
        # logger.info("Attribution class initializing")
        # save data to state
        for field in sm["attribution"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])
        # self.clean_id()
        logger.debug("Attribution data: {}".format(self.__dict__))

    def get_data(self):
        return self.__dict__ # todo
