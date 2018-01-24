from __future__ import division, print_function
import logging
import sys
sys.path.append('')
from spec_mapping import mapping as sm
logger = logging.getLogger(__name__)
from unit import Unit


class Sequence(Unit):

    def __init__(self, CONFIG, data_dictionary, sample_obj):
        super(Sequence, self).__init__()
        self.unit_type = "sequence"
        # logger.info("Sequence class initializing")
        self.CONFIG = CONFIG
        self.save_sequence_data_to_state(data_dictionary, sm["sequence"])
        self.clean_id(sample_obj)

        logger.debug("Sequence data (sans the actual sequence): {}".format({k:v for k, v in self.__dict__.iteritems() if k != "sequence"}))

        if hasattr(sample_obj, "sample_id"):
            # Add parent/child connections with sample_obj if sample_obj is something
            try:
                self.parent = sample_obj
                self.parent.children.append(self)
                logger.debug("Set parent/child connections between {} (self) and {} (parent).".format(self.sequence_id, self.parent.sample_id))
            except:
                logger.error("Could not set parent for sequence {}.".format(self.sequence_id))

    def save_sequence_data_to_state(self, data_dictionary, spec):
        for field in spec:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

    def clean_id(self, sample_obj):
        # logger.warn("this function must be replaced once cleaning function interface is up")
        if hasattr(self, "sample_id"):
            if hasattr(sample_obj, "sample_id"):
                if self.sample_id is not sample_obj.sample_id:
                    logger.error("Mismatch between (given) sample_id and that of the sample_obj. Throwing away sequence object.")
                    delattr(self, "sample_id")
                    return;
        else:
            if hasattr(sample_obj, "sample_id"):
                self.sample_id = sample_obj.sample_id
            else:
                return

        if not hasattr(self, "accession"):
            logger.warn("missing accession. Making it up.")
            self.accession = "unknown_accession"
        sequence_id = self.sample_id + '|' + self.accession
        if hasattr(self, "sequence_id") and self.sequence_id is not sequence_id:
            logger.error("Sequence ID provided does not match expected. Continuing, but expect errors.")
        self.sequence_id = sequence_id

    def is_valid(self):
        return hasattr(self, "sequence_id") and hasattr(self, "sequence")
