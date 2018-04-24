from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.append('')
from unit import Unit


class Attribution(Unit):

    def __init__(self, CONFIG, data_dictionary):
        """saves data provided and sets attribution_id"""
        super(Attribution, self).__init__()
        self.unit_type = "attribution"
        self.CONFIG = CONFIG

        sm = CONFIG["mapping"]
        for field in sm["attribution"]:
            if field in data_dictionary.keys():
                setattr(self, field, data_dictionary[field])

        ## init must set attribution_id
        if not hasattr(self, "attribution_id"):
            setattr(self, "attribution_id", self.authors)

    def is_valid(self):
        return hasattr(self, "attribution_id") and self.attribution_id is not None #pylint: disable=E1101
