from __future__ import division, print_function
import logging
from strain import Strain
from sample import Sample
from sequence import Sequence
# from titer import Titer
from attribution import Attribution
logger = logging.getLogger(__name__)

class Cluster:

    def __init__(self, data_dictionary, cluster_type="genic"):
        logger.info("Cluster class initializing. Type={}".format(cluster_type))
        self.strains = set()
        self.samples = set()
        self.sequences = set()
        self.attributions = set()
        self.titers = set()

        if cluster_type == "attribution":
            d = Attribution(data_dictionary)
            # Operations
            self.attributions.add(d)
        # elif cluster_type == "titer":
        #     w = Titer(data_dictionary)
        #     # Operations
        #     self.titers.add(w)
        else:
            a = Strain(data_dictionary)
            b = Sample(data_dictionary, a)
            y = Sequence(data_dictionary, b)
            # Add to self
            if a.is_valid():
                self.strains.add(a)
            self.samples.add(b)
            self.sequences.add(y)

        pass

    def get_all_accessions(self):
        return [s.accession for s in self.sequences if hasattr(s, "accession")]

    def clean(self):
        logger.warn("unimplemented cluster.clean method")
