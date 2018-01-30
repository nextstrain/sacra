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

        ## add parent / child links
        messy_flag = False
        try:
            self.parent = strain_obj
            self.parent.children.append(self)
        except:
            messy_flag = True

        # fix the strain_name and create the strain_id
        if hasattr(self, "strain_id") and hasattr(self, "parent") and self.parent.strain_id != selt.strain_id:
            logger.error("Mismatched strain id between sample ({}) and it's parent ({})".format(self.strain_id, self.parent.strain_id))
        elif hasattr(self, "sample_id"):
            if hasattr(self, "parent"):
                if "|".join(self.sample_id.split('|')[0:2]) != self.parent.strain_id:
                    logger.error("Mismatched sample_id in sample ({}) and parent ({})".format(self.sample_id, self.parent.strain_id))
        else:
            if not hasattr(self, "strain_id"):
                if hasattr(strain_obj, "strain_id"):
                    self.strain_id = strain_obj.strain_id
                else:
                    logger.error("Can't find / make the strain_id in the sample object. Bad.")
                    return
            self.fix_single("sample_name")
            setattr(self, "sample_id", "{}|{}".format(self.strain_id, self.sample_name))

        if messy_flag:
            logger.error("Could not set parent for sample {}.".format(self.sample_id))

    def is_valid(self):
        return hasattr("sample_id") and hasattr("strain_id")
