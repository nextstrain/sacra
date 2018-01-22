import logging
import sys
sys.path.append('')
from spec_mapping import mapping as sm
logger = logging.getLogger(__name__)

class Sequence:

    def __init__(self, data_dictionary):
        logger.info("Sequence class initializing")
        self.save_sequence_data_to_state(data_dictionary, sm)
        self.sort_out_sequence_id()
        print(dir(self))

    def save_sequence_data_to_state(self, data_dictionary, spec_mapping):
        for field in spec_mapping["sequence"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

    def sort_out_sequence_id(self):
        if not hasattr(self, "sequence_id"):
            logger.warn("No sequence ID found for {}, building.".format("some accession"))
            # construct name from cleaning function

    def is_valid(self):
        return True
