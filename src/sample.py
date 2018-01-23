from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.append('')
from spec_mapping import mapping as sm

class Sample:

    def __init__(self, data_dictionary, strain_obj):
        # logger.info("Sample class initializing")
        # save data to state
        for field in sm["sample"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

        self.clean_id(strain_obj)
        logger.debug("Sample data: {}".format(self.__dict__))

    def is_valid(self):
        return hasattr("sample_id") and hasattr("strain_id")

    def clean_id(self, strain_obj):
        # step 1: get the strain_id
        if not hasattr(self, "strain_id"):
            if hasattr(strain_obj, "strain_id"):
                self.strain_id = strain_obj.strain_id
            else:
                logger.error("Can't find / make the strain_id in the sample object. Bad.")
                return
        if not hasattr(self, "sample_name"):
            logger.warn("No sample name. Making it up...")
            self.sample_name = "unknown_sample"
        setattr(self, "sample_name", "{}|{}".format(self.strain_id, self.sample_name))

    def get_data(self):
        return self.__dict__ # todo
