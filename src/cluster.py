from __future__ import division, print_function
import sys
import logging
from strain import Strain
from sample import Sample
from sequence import Sequence
# from titer import Titer
from attribution import Attribution
logger = logging.getLogger(__name__)
flatten = lambda l: [item for sublist in l for item in sublist]

class Cluster:

    def __init__(self, CONFIG, data_dictionary, cluster_type="genic"):
        # logger.info("Cluster class initializing. Type={}".format(cluster_type))
        self.CONFIG = CONFIG
        self.cluster_type = cluster_type
        if self.cluster_type == "genic":
            self.strains = []
            self.samples = []
            self.sequences = []
            a = Strain(self.CONFIG, data_dictionary)
            b = Sample(self.CONFIG, data_dictionary, a)
            y = Sequence(self.CONFIG, data_dictionary, b)

            ## set links between a, b, c - only if the object is valid

            ## add to state (self) if the object is valid
            if a.is_valid():
                self.strains.append(a)
            self.samples.append(b)
            self.sequences.append(y)
        elif self.cluster_type == "titer":
            self.titers = []
            # w = Titer(data_dictionary)
            # Operations
            # self.titers.append(w)
        elif self.cluster_type == "attribution":
            self.attributions = []
            d = Attribution(self.CONFIG, data_dictionary)
            # Operations
            self.attributions.append(d)
        elif self.cluster_type == "unlinked":
            self.strains = []
            self.samples = []
            self.sequences = []
        else:
            logger.error("Unknown cluster_type {}".format(cluster_type))


    def get_all_units(self):
        if self.cluster_type == "genic":
            return flatten([list(self.strains), list(self.samples), list(self.strains)])
        elif self.cluster_type == "titer":
            return list(self.titers)
        elif self.cluster_type == "attribution":
            return list(self.attributions)

    def is_valid(self):
        """ are any of the units contained within this cluster valid? """
        if self.cluster_type == "genic":
            return True ## to implement
        elif self.cluster_type == "titer":
            return True ## to implement
        elif self.cluster_type == "attribution":
            if len(self.attributions) != 1:
                return False
            else:
                return next(iter(self.attributions)).is_valid()

    def get_all_accessions(self):
        if self.cluster_type != "attribution":
            return [s.accession for s in self.sequences if hasattr(s, "accession")]
        else:
            return []

    def clean(self):
        ### STEP 1: MOVE

        ### STEP 2: FIX
        logger.debug("fix (cluster type: {})".format(self.cluster_type))
        [unit.fix() for unit in self.get_all_units()]
        ### STEP 3: CREATE

        ### STEP 4: DROP
