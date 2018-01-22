import logging
from strain import Strain
from sample import Sample
from sequence import Sequence
# from titer import Titer
from attribution import Attribution
logger = logging.getLogger(__name__)

class Cluster:

    def __init__(self, data_dictionary, cluster_type="genic"):
        logger.info("Cluster class initializing")
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
            b = Sample(data_dictionary)
            y = Sequence(data_dictionary)
            if not hasattr(b, "strain_id") and hasattr(a, "strain_id"):
                b.strain_id = a.strain_id
            if not hasattr(y, "sample_id") and hasattr(b, "sample_id"):
                y.sample_id = b.sample_id
            # Operations x3


            # Add to self
            if a.is_valid():
                self.strains.add(a)
            self.samples.add(b)
            self.sequences.add(y)

        pass
