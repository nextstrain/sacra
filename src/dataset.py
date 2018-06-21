"""Sacra dataset object class.

This module defines a Dataset class, the fundamental unit of a Sacra run.
A Dataset object acts as a structured container for sequence and titer data,
as well as associated metadata. Metadata is separated into three basic
divisions representative of biological phenomena and linked in a
one-to-many-to-many fashion:

    1. Strain: a single strain of pathogen in a single host organism. If two
        samples/sequences share a strain, it means they came from the same
        infection in the same host, or were grown in the same culture.
    2. Sample: a sampling event of a given strain. Multiple samples
        can be drawn from a single strain, separated either physically within-
        host (e.g. serum and urine samples) or temporally in the case of
        chronic infections.
    3. Sequence: a nucleotide sequnce produced by a sequencing run. One sample
        may give rise to multiple sequences.

Each sequence may be additionally linked to attribution information.

Todo:
    * Writing to Fasta (full headers)
    * Writing to Fasta (augur headers) + metadata TSV
    * Reading from Sacra JSON format
    * Parsing of TSV/CSV metadata tables (e.g. from GISAID)
    * Titer handling
"""
from __future__ import division, print_function
import json
import logging
from strain import Strain
from sample import Sample
from sequence import Sequence
# from titer import Titer
from attribution import Attribution
from metadata import Metadata

logger = logging.getLogger(__name__)

class Dataset(object):
    """Wrapper class that links, cleans, and stores data.

    A Dataset object can also inject metadata derived from auxiliary files
    and write its data to new files.
    """

    def __init__(self, CONFIG):
        """Initialize a dataset object.

        No functions are called at the time of initialization, and the only
        non-empty class attribute at the time of initialization is the
        pathogen-specific config file that controls the run.
        """
        logger.info("Dataset initializing.")
        self.CONFIG = CONFIG
        self.logger = logger

        # All types of units that a Dataset can handle are initilized
        # as empty lists
        self.strains = []
        self.samples = []
        self.sequences = []
        self.attributions = []
        self.titers = []
        self.metadata = []

        self.invalid_units = []

    def make_units_from_data_dictionaries(self, filetype, dicts):
        """Set linked units into state.

        Takes a list of dictionaries and converts the metadata stored within them
        into three data units (four if attribution information is included).

        Each dictionary is created by parsing primary input files and maps
        field names to metadata, with field names being derived from the spec
        in the CONFIG dictionary.

        Todo:
            * Ensure that this works for JSON input files
        """
        logger.info("Making units from filetype {} & data".format(filetype))

        for data_dict in dicts:
            # Initialize Strain, Sample, and Sequence objects.
            # Parent/child links are initialized by passing Strain/Sample
            # ojbects to Sample/Sequence initializers.
            strain_obj = Strain(self.CONFIG, data_dict)
            sample_obj = Sample(self.CONFIG, data_dict, strain_obj)
            sequence_obj = Sequence(self.CONFIG, data_dict, sample_obj)

            # Add new Strain, Sample, Sequence objects to state
            self.strains.append(strain_obj)
            self.samples.append(sample_obj)
            self.sequences.append(sequence_obj)

            # Handle Attributions if they exist, or set attribution to None
            if "authors" not in data_dict.keys():
                data_dict["authors"] = None
            attribution_obj = Attribution(self.CONFIG, data_dict)
            self.attributions.append(attribution_obj)
            # Manually link sequences with their attribution
            attribution_obj.parent = sequence_obj
            sequence_obj.children.append(attribution_obj)

            # Validate that parent/child links are of the correct type
            # self.validate_unit_links()

    def validate_unit_links(self):
        """Ensure that all unit links are of the proper number and type.

        Strains:
            * Should not have a parent (i.e. parent is None)
            * Should have one or more children

        Samples:
            * Should have a parent of type Strain
            * Should have one or more children

        Sequences:
            * Should have a parent of type Sample
            * Should have zero or one children

        Attributions:
            * Should have a parent of type Sequence
            * Should not have any children (i.e. children == [])

        Todo:
            As a separate function, create a checker for titers.
        """
        try:
            for strain in self.strains:
                try:
                    assert strain.parent is None
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
                    assert not attribution.children
                except AssertionError:
                    logger.critical("Error linking w.r.t. attribution {}".format(attribution))
                    raise Exception
        except:
            # On failure, open a debugger.
            # At some point this should be handled by a better error handler.
            import pdb; pdb.set_trace()

    def clean_data_units(self):
        """Apply config-defined cleaning functions to each unit."""
        logger.info("Cleaning all primary data units")
        [ unit.fix() for unit in self.get_all_units() ]

    def make_metadata_units(self, tag, dicts):
        """Create new metadata units from dictionaries, append to state.

        Similar to make_units_from_data_dictionaries, but does not require
        parent/child relationships, as metadata will be injected to existing
        units with preexisting links.
        """
        logger.info("Making metadata units based on tag: {}".format(tag))
        for d in dicts:
            self.metadata.append(Metadata(self.CONFIG, tag, d))

    def apply_command_line_arguments_everywhere(self, cmdargs):
        """Apply specific metadata, specified at cmd line, to all units.

        This will most often be used for attribution information, and does
        not use metadata units as their injection only happens once per unit.
        This, instead applies to all strains (therefore all downstream units).
        """
        for key in cmdargs.keys():
            for strain in self.strains:
                strain.setprop(key, cmdargs[key])

    def clean_metadata_units(self):
        """Apply cleaning functions to metadata units."""
        # TODO: This needs to be fixed with better smart setters and getters
        logger.info("Cleaning metadata units")
        [unit.fix() for unit in self.metadata]

    def inject_metadata_into_data(self):
        """Add metadata stored in Metadata units to primary dataset.

        Metadata are injected at a certain 'level' based on their tag to
        avoid duplicate injection. Only valid fields (i.e. fields defined
        within the config) are applied.

        Todo:
            * Inject metadata units that are not tagged 'accession'
        """
        # Define all valid fields from the config
        # Remove '_id' fields, as they are handled separately later
        vf = self.CONFIG['mapping']['strain'] + self.CONFIG['mapping']['sample'] + self.CONFIG['mapping']['sequence'] + self.CONFIG['mapping']['attribution']
        logger.info("injecting metadata")
        vf = [ field for field in vf if not field.endswith('_id')]

        # Iterate over all metadata units, and inject if they match on the
        # proper field for their tag
        for m  in self.metadata:
            if m.tag == 'accession':
                for s in self.sequences:
                    if m.accession == s.accession:
                        self.inject_single_meta_unit(m, s, vf)

    def inject_single_meta_unit(self, meta, unit, valid_fields):
        """For all valid fields in a given unit, inject them using setprop.

        Fields are considered valid if they are defined in the config.

        Setprop will pseudo-recursively find the proper linked unit to which
        metadata should be applied."""
        # pylint: disable=R0201
        for field in valid_fields:
            if hasattr(meta, field):
                unit.setprop(field, getattr(meta, field), overwrite=False)

    def get_all_accessions(self):
        """Return a list of all accession names stored in state."""
        return [ seq.accession for seq in self.sequences ]

    def get_all_units(self):
        """Return a list of all non-metadata units stored in state."""
        return self.strains + self.samples + self.sequences + self.attributions

    def update_units_pre_merge(self):
        """Modify in place units that need to be re-cleaned using injected metadata.

        Todo:
            This method will need to be expanded for non-attribution units and
            made to be programmatic.
        """

        for attr in self.attributions:
            if attr.attribution_id is None:
                attr.attribution_id = self.CONFIG['pre_merge_fix_functions']['attribution']['attribution_id'](attr, attr.attribution_id, logger)

            attr.parent.attribution_id = attr.attribution_id

    def merge_units(self):
        """Modify unit parent/child links to create a tree of matching IDs.

        The list 'types' is ordered so that more basal units are merged first,
        ensuring that the treelike structure of units (other than attributions)
        is maintined.
        """
        types = ['strains', 'samples', 'sequences', 'attributions', 'titers']
        for t in types:
            self.merge_on_unit_type(t)

    def merge_on_unit_type(self, unit_type):
        """Merge units of a given unit type if they have matching primary keys.

        Options for unit types are: strain, sample, sequence, attribution, and titer.

        """
        logger.info("Merging on {}".format(unit_type))
        out = []

        # Make all pairwise comparisons of units of the same type
        units = getattr(self, unit_type)
        for i in range(len(units)-1):
            for j in range(i+1, len(units)):

                # Ignore units that have already been merged out (i.e. merged with)
                # another unit, but not yet removed from the list of units.
                if units[j] not in out:
                    first = units[i]
                    second = units[j]

                    # Catch for duplicated unit bug.
                    assert first is not second, logger.error("Error. Tried to match \
                        unit with itself.")

                    # Find names of the two units, if both exist and they match,
                    # merge the units.
                    first_id = getattr(first, "{}_id".format(unit_type[:-1]))
                    second_id = getattr(second, "{}_id".format(unit_type[:-1]))
                    if first_id is None or second_id is None:
                        continue
                    if first_id == second_id:
                        logger.debug("Merging units with matching ID: {}".format(first_id))
                        self.merge_two_units(first, second)

                        # After the merge, add the second unit to a 'to be removed' list.
                        out.append(second)

        # Remove all the merged units from lists in state
        out = list(set(out))
        for bad in out:
            units.remove(bad)
        setattr(self, unit_type, units)
        logger.info("Merged {} {} units based on matching IDs (not necessarily all the same IDs)".format(len(out), unit_type))

    def merge_two_units(self, unit1, unit2):
        """Merge two units of the same type with the same key.

        Keys are will be <unit_type>_id field in the unit's state.

        There are two major steps for merge_two_units:
            1. Make sure that the units share a parent. If they do, append all the
               children of unit2 to the children of unit1.
            2. Add metadata fields described in unit2 to unit1, if they do not
               already exist.

        Todo:
            * At the moment, if two metadata fields are in conflict, the merge
              will default to the first in the list (which is very arbitrary).
              There should be a more reasoned way of choosing which metadata field
              is correct, or of aborting the merge if the units are being merged
              erroneously.
        """
        assert unit1.unit_type == unit2.unit_type, logger.error("Attempted to merge 2 units with different types: {} & {}".format(unit1.unit_type, unit2.unit_type))

        # Set parents/children
        if unit1.unit_type != "attribution":
            try:
                # This check covers the rare case that two units have the same ID,
                # since IDs are programatically derived they are not necessarily unique.
                assert unit1.parent == unit2.parent, logger.error("Attempted to merge 2 units with different parents: {} and {}".format(unit1.parent, unit2.parent))
            except:
                raise TypeError
        unit1.children.extend(unit2.children)

        # Overwrite metadata
        for field in self.CONFIG["mapping"][unit1.unit_type]:
            if hasattr(unit2, field) and (not hasattr(unit1, field)):
                setattr(unit1, field, getattr(unit2, field))
            elif hasattr(unit1, field) and hasattr(unit2, field):
                _f1 = getattr(unit1, field)
                _f2 = getattr(unit2, field)
                # Report to the user if there is a potential conflict in metadata
                if _f1 != _f2:
                    u1id = getattr(unit1, "{}_id".format(unit1.unit_type))
                    logger.warn("Units with matching ID {} have mismatching {}:\n\
                        1. {}\n\
                        2. {}\n\
                        Defaulting (possibly incorrectly) to (1).".format(u1id, field, _f1, _f2))

    def get_all_metadata_fields(self):
        """Return a list of all possible metadata fields."""
        return self.CONFIG["mapping"]["strain"] + self.CONFIG["mapping"]["sample"] + self.CONFIG["mapping"]["sequence"] + self.CONFIG["mapping"]["attribution"]

    def validate_units(self):
        """Ensure that all units in self are valid according a suite of tests.

        Current tests:
            * ensure_metadata_assignment: make sure that metadata is assigned
              to the correct unit types, and if not, move it as necessary.
        """
        all_fields = self.get_all_metadata_fields()
        for unit in self.get_all_units():
            unit.ensure_metadata_assignment(all_fields, self)

    def write_valid_units_to_json(self, filename):
        """Write all fields in the config to a JSON according to the Sacra spec.

        Todo:
            * Handling for titers.
        """
        logger.info("Writing to JSON: {}".format(filename))
        data = {"strains": [], "samples": [], "sequences": [], "attributions": []}
        data["dbinfo"] = {"pathogen": self.CONFIG["pathogen"]}
        for n in ["strains", "samples", "sequences", "attributions"]:
            if hasattr(self, n): # if, e.g., "sequences" (n) is in the self
                data[n].extend([x.get_data() for x in getattr(self, n) if x.is_valid()])
        # Remove empty values
        for table in data:
            if table == "dbinfo":
                continue
            for block in data[table]:
                for key in block.keys():
                    if block[key] in [None, '', '?', 'unknown', "Unknown"]:
                        del block[key]
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, ensure_ascii=False)

    def write_valid_units_to_fasta(self, filename, tsv_metadata=False):
        """Write all sequences in the dataset to a Fasta file."""
        all_fields = self.get_all_metadata_fields()
        augur_headers = ['strain_id', 'pathogen', 'accession', 'collection_date', 'region', 'country', 'division', 'location', 'submitting_lab', 'host_age', 'host_gender']
        with open(filename, 'w') as f:
            for accession in self.sequences:
                line = '>{}\n'.format(accession.getprop('sequence_id')[0])
                f.write(line)
                f.write(accession.getprop('sequence')[0]+'\n')
        if tsv_metadata:
            tsv_filename = filename.split('.')[0]+'.tsv'
            with open(tsv_filename, 'w') as f:
                head = 'sequence_id\t' + '\t'.join(augur_headers) + '\n'
                f.write(head)
                for accession in self.sequences:
                    line = accession.getprop('sequence_id')[0]
                    for header in augur_headers:
                        if accession.hasprop(header):
                            line = line + '\t{}'.format(accession.getprop(header)[0])
                        else:
                            line = line + '\tNone'
                    line = line + '\n'
                    f.write(line)

    def write_invalid_units(self, filename):
        """Write units flagged as invalid to a separate JSON.

        This JSON still needs to have a spec before this QOL function can be written.
        """
        pass
