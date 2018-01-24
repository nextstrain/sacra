from __future__ import division, print_function
import logging
from strain import Strain
from sample import Sample
from sequence import Sequence
# from titer import Titer
from attribution import Attribution
logger = logging.getLogger(__name__)

class Cluster:

    def __init__(self, CONFIG, data_dictionary, cluster_type="genic"):
        logger.info("Cluster class initializing. Type={}".format(cluster_type))
        self.CONFIG = CONFIG
        self.cluster_type = cluster_type
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
            a = Strain(self.CONFIG, data_dictionary)
            b = Sample(data_dictionary, a)
            y = Sequence(data_dictionary, b)
            # Add to self
            if a.is_valid():
                self.strains.add(a)
            self.samples.add(b)
            self.sequences.add(y)

    def get_all_accessions(self):
        return [s.accession for s in self.sequences if hasattr(s, "accession")]

    def clean(self):
        ### STEP 1: MOVE

        ### STEP 2: FIX
        logger.debug("fix (cluster type: {})".format(self.cluster_type))
        [strain.fix() for strain in self.strains]
        ### STEP 3: CREATE

        ### STEP 4: DROP
