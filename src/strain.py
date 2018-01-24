from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys, os
sys.path.append('')
from spec_mapping import mapping as sm

class Strain:

    def __init__(self, CONFIG, data_dictionary):
        # logger.info("Strain class initializing")
        self.CONFIG = CONFIG
        # save data to state
        for field in sm["strain"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

        self.ensure_id()
        logger.debug("Strain data: {}".format(self.__dict__))

    def ensure_id(self):
        if not hasattr(self, "strain_id"):
            if hasattr(self, "strain_name"):
                ## check if there is a fix function!
                if "strain_name" in self.CONFIG["fix_functions"]:
                    self.strain_name = self.CONFIG["fix_functions"]["strain_name"](self.strain_name, logger)
                self.strain_id = self.strain_name
            else:
                logger.error("Neither strain_name not strain_id!")

    # def get_fields(self):
    #     vars()

    def move(self):
        ## move names. I'm guessing this will need to use self.parent & self.child methods
        pass

    def fix(self):
        ## fix names.
        for name in vars(self):
            try:
                setattr(self, name, self.CONFIG["fix_functions"][name](getattr(self, name), logger))
            except KeyError:
                pass

    def create(self):
        ## create fields as desired
        pass

    def drop(self):
        ## drop values. This is dangerous - make sure all objects.move() have completed
        pass

    def is_valid(self):
        return hasattr(self, "strain_id")

    def get_data(self):
        return {k:v for k, v in self.__dict__.iteritems() if k is not "CONFIG"}
