"""Sacra control script.

This module serves as the command line interface with which users will
interact. This module works in tandem with a pathogen-specific config
(specified in sacra/configs) initialize a Dataset object from a set of
input files, inject additional metadata, canonicalize metadata in the
dataset, and write to JSON.

Example:
    Sacra can be run to build a JSON from a set of FASTA files, with
    metadata being provided via entrez. Required inputs are one or
    more input files, one output file, and a pathogen name (e.g. zika).
    Additionally, there must be a config file in sacra/configs that
    correlates with the listed pathogen name::

        $ python src/run.py -f test/input/zika_test.fasta \
        -o test/output/zika_test.json --pathogen zika

Attributes:
    parser (ArgumentParser) : Handler for all command line arguments that
    control a Sacra run. Included within the parser are two subparsers to
    handle metadata (1) from entrez and (2) from files and command line
    arguments.

Todo:
    * Add accession list handling to run script (needs to be added
    to dataset.py as well)
    * Add handling for other output file formats (such as FASTA)

"""
from __future__ import division, print_function
import logging
import argparse
import sys
sys.path.append('')
from dataset import Dataset
from utils.colorLogging import ColorizingStreamHandler
from utils.read_datafile_to_dictionaries import read_datafile_to_dictionaries
from utils.read_metafile_to_dictionaries import read_metafile_to_dictionaries
from entrez import retrieve_entrez_metadata

parser = argparse.ArgumentParser(description="Cleaning & combining of genomic & titer data")
parser.add_argument("--debug",
                    action="store_const",
                    dest="loglevel",
                    const=logging.DEBUG,
                    help="Enable debugging logging")
parser.add_argument("--datafiles", "-f",
                    type=str,
                    nargs='*',
                    default=[],
                    dest="datafiles",
                    help="primary data file types: text (list of accessions), FASTA, JSON")
parser.add_argument("--metafiles", "-m",
                    default=[],
                    dest="metafiles",
                    type=str,
                    nargs='*',
                    help="metadata file types: CSV, TSV, XLS")
parser.add_argument("--pathogen",
                    required=True,
                    type=str,
                    help="this sets the config file")
# parser.add_argument("--accession_list",
#                     default=[],
#                     type=str,
#                     nargs='*',
#                     help="list of strings to query genbank with") #TODO: Implement accession list input
parser.add_argument("-o", "--outfile",
                    default="output/test_output.json",
                    help="name of output file (requires full path)")

group = parser.add_argument_group('entrez')
group.add_argument("--use_entrez_to_improve_data", "--entrez",
                   dest="use_entrez_to_improve_data",
                   action="store_true",
                   help="Query genbank for all accessions to help clean / correct metadata data")

# group = parser.add_argument_group('overwrites')
# group.add_argument("--overwrite_fasta_header",
#                     type=str,
#                     help="Overwrite the config-defined FASTA header")

group = parser.add_argument_group('metadata')
group.add_argument('--custom_fasta_header',
                   default=None,
                   type=str,
                   help='custom fasta header field name assigned in pathogen config')
group.add_argument('-c', '--custom_fields',
                   default=[],
                   type=str,
                   nargs='*',
                   help='fields that should be added to full sacra build in format field_name:"field value"')

def provision_directories(logger):
    """Build input and output directories if they don't exist."""
    import os
    if not os.path.isdir('test/output'):
        logger.info("Directory no ./test/output directory found; creating.")
        os.makedirs('test/output')
    if not os.path.isdir('input'):
        logger.info("Directory no ./input directory found; creating.")
        os.makedirs('input')
    if not os.path.isdir('output'):
        logger.info("Directory no ./output directory found; creating.")
        os.makedirs('output')

def get_all_accessions(d):
    """Return a list of all accessions present in the dataset."""
    return [ seq.accession for seq in d.sequences ]

def main(args, logger):
    """Primary sacra process.

    1. Import config as a properly formatted dict
    2. Initialize dataset, populate from primary input files
    3. Primary clean
    4. Import metadata from secondary sources to units:
        i. Secondary metafiles
        ii. Entrez
        iii. Command line fields (applied to all units in dataset)
    5. Secondary clean
    6. Inject metadata units and reorganize conflicting metadata
    7. Reduce dataset size by merging on primary keys
    8. Validate units
    9. Write to files (JSON)
    """
    try:
        CONFIG = __import__("configs.{}".format(args.pathogen),
                            fromlist=['']).make_config(args, logger)
        assert isinstance(CONFIG, dict), logger.error("")
    except ImportError:
        logger.critical("Could not load config! File configs/{}.py must exist!".format(args.pathogen)); sys.exit(2)
    except AttributeError:
        logger.critical("Config file configs/{}.py must define a \"make_config\" function".format(args.pathogen)); sys.exit(2)
    except AssertionError:
        logger.critical("make_config() in configs/{}.py must return a dictionary".format(args.pathogen)); sys.exit(2)

    dataset = Dataset(CONFIG)
    for f in args.datafiles:
        (filetype, data_dictionaries) = read_datafile_to_dictionaries(f, CONFIG)
        dataset.make_units_from_data_dictionaries(filetype, data_dictionaries)

    dataset.clean_data_units()

    if args.metafiles:
        logger.info("Reading metadata files")
        for f in args.metafiles:
            (tag, list_of_dicts) = read_metafile_to_dictionaries(f)
            dataset.make_metadata_units(tag, list_of_dicts)

    if args.use_entrez_to_improve_data:
        accs = get_all_accessions(dataset)
        list_of_dicts = retrieve_entrez_metadata(accs, CONFIG)
        dataset.make_metadata_units("accession", list_of_dicts)

    if args.custom_fields:
        cmdargs = {}
        for cmdarg in args.custom_fields:
            key, value = cmdarg.split(':')[0], cmdarg.split(':')[1]
            cmdargs[key] = value
        dataset.apply_command_line_arguments_everywhere(cmdargs)

    if dataset.metadata:
        dataset.clean_metadata_units()
        dataset.inject_metadata_into_data()

        dataset.update_units_pre_merge()

    dataset.merge_units()

    dataset.validate_units()

    valid_file = args.outfile
    invalid_file = 'output/invalid.json'
    dataset.write_valid_units_to_json(valid_file)
    dataset.write_invalid_units(invalid_file)

if __name__ == "__main__":
    """Initialize command line arguments, parser, and begin build.

    Logger derived from: https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters
    """
    ARGS = parser.parse_args()

    root_logger = logging.getLogger('')
    root_logger.setLevel(ARGS.loglevel if ARGS.loglevel else logging.INFO)
    root_logger.addHandler(ColorizingStreamHandler())
    LOGGER = logging.getLogger(__name__)

    provision_directories(LOGGER)
    main(ARGS, LOGGER)
