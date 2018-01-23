from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys, os
sys.path.append('')
from spec_mapping import mapping as sm

class Strain:

    def __init__(self, data_dictionary):
        # logger.info("Strain class initializing")
        # save data to state
        for field in sm["strain"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

        self.clean_id()
        logger.debug("Strain data: {}".format(self.__dict__))

    def clean_id(self):
        if not hasattr(self, "strain_id"):
            if hasattr(self, "strain_name"):
                self.strain_id = self.strain_name
            else:
                logger.error("Neither strain_name not strain_id!")

    def is_valid(self):
        return hasattr(self, "strain_id")

    def get_data(self):
        return self.__dict__ # todo
