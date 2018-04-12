from __future__ import division, print_function
import logging
logger = logging.getLogger(__name__)

import json
import os, sys
from strain import Strain
from sample import Sample
from sequence import Sequence
# from titer import Titer
from attribution import Attribution
from metadata import Metadata

class Dataset:

    # Initializer
    def __init__(self, CONFIG):
        logger.info("Dataset init")
        self.CONFIG = CONFIG
        self.logger = logger
        self.strains = []
        self.samples = []
        self.sequences = []
        self.attributions = []
        self.titers = []
        self.metadata = []
        # populate_lookups(self.CONFIG)

    def make_units_from_data_dictionaries(self, filetype, dicts):
        """
        sets linked units into state
        """
        logger.info("Making units from filetype {} & data {}".format(filetype, dicts))

        dummy_strain = Strain(self.CONFIG, dicts[0])
        dummy_sample = Sample(self.CONFIG, dicts[0], dummy_strain)
        dummy_sequence = Sequence(self.CONFIG, dicts[0], dummy_sample)
        dummy_attribution = Attribution(self.CONFIG, dicts[0])
        dummy_sequence.children.append(dummy_attribution)
        dummy_attribution.parent = dummy_sequence
        self.strains.append(dummy_strain)
        self.samples.append(dummy_sample)
        self.sequences.append(dummy_sequence)
        self.attributions.append(dummy_attribution)
        try:
            for strain in self.strains:
                try:
                    assert strain.parent == None
                    assert len(strain.children) >= 1
                except AssertionError:
                    logger.critical("Error linking w.r.t. strain {}".format(strain))
                    raise Exception
            for sample in self.samples:
                try:
                    assert isinstance(sample.parent, Strain)
                    assert len(sample.children) >= 1
                except AssertionError:
                    logger.critical("Error linking w.r.t. sample {}".format(sample))
                    raise Exception
            for sequence in self.sequences:
                try:
                    assert isinstance(sequence.parent, Sample)
                    assert len(sequence.children) == 1
                except AssertionError:
                    logger.critical("Error linking w.r.t. sequence {}".format(sequence))
                    raise Exception
            for attribution in self.attributions:
                try:
                    assert isinstance(attribution.parent, Sequence)
                    assert len(attribution.children) == 0
                except AssertionError:
                    logger.critical("Error linking w.r.t. attribution {}".format(attribution))
                    raise Exception
        except:
            import pdb; pdb.set_trace()


    def clean_data_units(self):
        logger.info("CLEAN DATA UNITS")

    def clean_metadata_units(self):
        logger.info("CLEAN METADATA UNITS")

    def inject_metadata_into_data(self):
        logger.info("injecting metadata")
        for u in self.metadata:
            if u.tag == "accession":
                for sequence in self.sequences:
                    if sequence.accession == u.accession:
                        setattr(sequence.parent, "country", u.country)


    def make_metadata_units(self, tag, dicts):
        logger.info("Making metadata uinit for {} {}".format(tag, dicts))
        for d in dicts:
            self.metadata.append(Metadata(self.CONFIG, tag, d))

    def get_all_accessions(self):
        return ['ACC1']


    def merge_units(self):
        pass

    def validate_units(self):
        pass

    def write_valid_units(self):
        pass

    def write_invalid_units(self):
        pass
