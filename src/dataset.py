from __future__ import division, print_function
import os, sys
from strain import Strain
from sample import Sample
from sequence import Sequence
# from titer import Titer
from attribution import Attribution
from metadata import Metadata
import json
import logging
logger = logging.getLogger(__name__)
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
        logger.info("Making units from filetype {} & data".format(filetype))
        for data_dict in dicts:
            dummy_strain = Strain(self.CONFIG, data_dict)
            dummy_sample = Sample(self.CONFIG, data_dict, dummy_strain)
            dummy_sequence = Sequence(self.CONFIG, data_dict, dummy_sample)
            self.strains.append(dummy_strain)
            self.samples.append(dummy_sample)
            self.sequences.append(dummy_sequence)
            if "authors" not in data_dict.keys():
                data_dict["authors"] = None
            dummy_attribution = Attribution(self.CONFIG, data_dict)
            self.attributions.append(dummy_attribution)
            dummy_attribution.parent = dummy_sequence
            dummy_sequence.children.append(dummy_attribution)
            self.validate_unit_links()

    def validate_unit_links(self):
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
                    assert len(sequence.children) < 2
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
        [unit.fix() for unit in self.get_all_units()]

    def make_metadata_units(self, tag, dicts):
        logger.info("Making metadata units based on tag: {}".format(tag))
        for d in dicts:
            self.metadata.append(Metadata(self.CONFIG, tag, d))

    def apply_command_line_arguments_everywhere(self, cmdargs):
        for key in cmdargs.keys(): # read straight from command line args
            for strain in self.strains:
                strain.setprop(key, cmdargs[key])

    def clean_metadata_units(self):
        # TODO: This needs to be fixed with better smart setters and getters
        # logger.info("CLEAN METADATA UNITS")
        # [unit.fix() for unit in self.metadata]
        pass

    def inject_metadata_into_data(self):
        vf = self.CONFIG['mapping']['strain'] + self.CONFIG['mapping']['sample'] + self.CONFIG['mapping']['sequence'] + self.CONFIG['mapping']['attribution']
        logger.info("injecting metadata")
        for m  in self.metadata:
            if m.tag == 'accession':
                for s in self.sequences:
                    if m.accession == s.accession:
                        self.inject_single_meta_unit(m, s, vf)

    def inject_single_meta_unit(self, meta, unit, valid_fields):
        for field in valid_fields:
            if hasattr(meta, field):
                unit.setprop(field, getattr(meta, field))

    def get_all_accessions(self):
        return ['ACC1']

    def get_all_units(self):
        """ Return a list of all non-metadata units stored in state."""
        return self.strains + self.samples + self.sequences + self.attributions

    def update_units_pre_merge(self):
        """Modify in place units that need to be re-cleaned using injected metadata.

        TODO: this method will need to be expanded for non-attribution units and
        made to be programmatic.
        """

        for attr in self.attributions:
            # import pdb; pdb.set_trace()
            if attr.attribution_id == None:
                attr.attribution_id = self.CONFIG['pre_merge_fix_functions']['attribution']['attribution_id']\
                    (attr, attr.attribution_id, logger)

            attr.parent.attribution_id = attr.attribution_id

    def merge_units(self):
        """Modify unit parent/child links to create a tree of matching IDs."""
        types = ['strains', 'samples', 'sequences', 'attributions', 'titers']
        for t in types:
            self.merge_on_unit_type(t)

    def merge_on_unit_type(self, unit_type):
        logger.info("Merging on {}".format(unit_type))
        out = []
        units = getattr(self, unit_type)
        for i in range(len(units)-1):
            for j in range(i+1, len(units)):
                if units[j] not in out:
                    first = units[i]
                    second = units[j]
                    assert first is not second, logger.error("Error. Tried to match \
                        unit with itself.")
                    first_id = getattr(first, "{}_id".format(unit_type[:-1]))
                    second_id = getattr(second, "{}_id".format(unit_type[:-1]))
                    if first_id is None or second_id is None:
                        continue
                    if first_id == second_id:
                        logger.debug("Merging units with matching ID: {}".format(first_id))
                        self.merge(first, second)
                        out.append(second)
        out = list(set(out))
        for bad in out:
            units.remove(bad)
        setattr(self, unit_type, units)
        logger.info("Merged {} {} units based on matching IDs (not necessarily all the same IDs)".format(len(out), unit_type))

    def merge(self, unit1, unit2):
        assert unit1.unit_type == unit2.unit_type, logger.error("Attempted to merge 2 units with different types: {} & {}".format(unit1.unit_type, unit2.unit_type))

        # Set parents/children
        if unit1.unit_type != "attribution":
            try:
                assert unit1.parent == unit2.parent, logger.error("Attempted to merge 2 units with different parents: {} and {}".format(unit1.parent, unit2.parent))
            except:
                return

        unit1.children.extend(unit2.children)

        # Overwrite metadata
        for field in self.CONFIG["mapping"][unit1.unit_type]:
            if hasattr(unit2, field) and (not hasattr(unit1, field)):
                setattr(unit1, field, getattr(unit2, field))
            elif hasattr(unit1, field) and hasattr(unit2, field):
                _f1 = getattr(unit1, field)
                _f2 = getattr(unit2, field)
                if _f1 != _f2:
                    u1id = getattr(unit1, "{}_id".format(unit1.unit_type))
                    logger.warn("Units with matching ID {} have mismatching {}:\n\
                        1. {}\n\
                        2. {}\n\
                        Defaulting (possibly incorrectly) to (1).".format(u1id, field, _f1, _f2))

    def validate_units(self):
        pass

    def write_valid_units(self, filename):
        logger.info("Writing to JSON: {}".format(filename))
        data = {"strains": [], "samples": [], "sequences": [], "attributions": []}
        data["dbinfo"] = {"pathogen": self.CONFIG["pathogen"]}
        for n in ["strains", "samples", "sequences", "attributions"]:
            if hasattr(self, n): # if, e.g., "sequences" (n) is in the self
                data[n].extend([x.get_data() for x in getattr(self, n) if x.is_valid()])
        # remove empty values
        for table in data:
            if table == "dbinfo":
                continue
            for block in data[table]:
                for key in block.keys():
                    if block[key] in [None, '', '?', 'unknown', "Unknown"]:
                        del block[key]
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, ensure_ascii=False)

    def write_invalid_units(self, filename):
        pass
