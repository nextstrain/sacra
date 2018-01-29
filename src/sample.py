from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.append('')
from unit import Unit

class Sample(Unit):

    def __init__(self, CONFIG, data_dictionary, strain_obj):
        super(Sample, self).__init__()
        self.unit_type = "sample"
        # logger.info("Sample class initializing")
        self.CONFIG = CONFIG
        # save data to state
        sm = CONFIG["mapping"]
        for field in sm["sample"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

        self.clean_id(strain_obj)
        # logger.debug("Sample data: {}".format(self.__dict__))

        if hasattr(strain_obj, "strain_id"):
            # Add parent/child connections with strain_obj if strain_obj is something
            try:
                self.parent = strain_obj
                self.parent.children.append(self)
                logger.debug("Set parent/child connections between {} (self) and {} (parent).".format(self.sample_id, self.parent.strain_id))
            except:
                logger.error("Could not set parent for sample {}.".format(self.sample_id))

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
        setattr(self, "sample_id", "{}|{}".format(self.strain_id, self.sample_name))
