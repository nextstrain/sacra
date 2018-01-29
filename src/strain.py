from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys, os
sys.path.append('')
from spec_mapping import mapping as sm
from unit import Unit

class Strain(Unit):
    def __init__(self, CONFIG, data_dictionary):
        super(Strain, self).__init__()
        self.unit_type = "strain"
        # logger.info("Strain class initializing")
        self.CONFIG = CONFIG
        # save data to state
        for field in sm["strain"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

        self.ensure_id()
        # logger.debug("Strain data: {}".format(self.__dict__))

    def ensure_id(self):
        """Ensure strain_id exists. So if there's strain_name, fix it, else create it. Then set strain_id as strain_name"""
        if not hasattr(self, "strain_id"):
            if hasattr(self, "strain_name"):
                self.fix_single("strain_name")
                self.strain_id = self.strain_name
            else:
                logger.error("Neither strain_name not strain_id! - create function not yet implemented (although I don't see how one could have this!)")

    def is_valid(self):
        return hasattr(self, "strain_id")
