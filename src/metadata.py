from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.append('')
from unit import Unit

class Metadata(Unit):

    def __init__(self, CONFIG, tag, metadict):
        super(Metadata, self).__init__()
        self.unit_type = "metadata"
        self.tag = tag
        for field in metadict:
            setattr(self, field, metadict[field])
