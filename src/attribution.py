from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.append('')
from spec_mapping import mapping as sm
from unit import Unit


class Attribution(Unit):

    def __init__(self, data_dictionary):
        super(Attribution, self).__init__()
        # logger.info("Attribution class initializing")
        # save data to state
        for field in sm["attribution"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])
        # self.clean_id()
        logger.debug("Attribution data: {}".format(self.__dict__))
