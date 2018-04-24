from __future__ import division, print_function
from dataset import Dataset
import logging
import argparse
import sys
sys.path.append('')
from utils.colorLogging import ColorizingStreamHandler
from utils.read_datafile_to_dictionaries import read_datafile_to_dictionaries
from utils.read_metafile_to_dictionaries import read_metafile_to_dictionaries
from entrez import retrieve_entrez_metadata


try:
    from pycallgraph import PyCallGraph
    from pycallgraph import Config
    from pycallgraph.output import GraphvizOutput
except:
    print("couldn't import pycallgraph and/or graphviz, skipping")

parser = argparse.ArgumentParser(description="Cleaning & combining of genomic & titer data")
parser.add_argument("--debug", action="store_const", dest="loglevel", const=logging.DEBUG, help="Enable debugging logging")
parser.add_argument("--datafiles", "-f", default=[], dest="datafiles", type=str, nargs='*', help="primary data file types: text (list of accessions), FASTA, JSON")
parser.add_argument("--metafiles", "-m", default=[], dest="metafiles", type=str, nargs='*', help="metadata file types: CSV, TSV, XLS")
parser.add_argument("--pathogen", required=True, type=str, help="This sets the config file")
# parser.add_argument("--accession_list", default=[], type=str, nargs='*', help="list of strings to query genbank with")
parser.add_argument("-o", "--outfile", default="output/test_output.json")
# parser.add_argument("--visualize_call_graph", action="store_true", default=False, help="draw a graph of calls being made")
# parser.add_argument("--call_graph_fname", default="output/graphviz_test.png", help="filename for call graph")
#
group = parser.add_argument_group('entrez')
group.add_argument("--use_entrez_to_improve_data", "--entrez", dest="use_entrez_to_improve_data", action="store_true", help="Query genbank for all accessions to help clean / correct metadata data")
#
# group = parser.add_argument_group('overwrites')
# group.add_argument("--overwrite_fasta_header", type=str, help="Overwrite the config-defined FASTA header")
#
group = parser.add_argument_group('metadata')
group.add_argument('--custom_fasta_header', default=None, type=str, help='custom fasta header field name assigned in pathogen config')
# group.add_argument('-c', '--custom_fields', default=[], type=str, nargs='*', help='fields that should be added to full sacra build in format field_name:"field value"')

def provision_directories(logger):
    import os
    if not os.path.isdir('input'):
        logger.info("Directory no ./input directory found; creating.")
        os.makedirs('input')
    if not os.path.isdir('output'):
        logger.info("Directory no ./output directory found; creating.")
        os.makedirs('output')

def get_all_accessions(d):
    return [ seq.accession for seq in d.sequences ]

def main(args, logger):
    try:
        CONFIG = __import__("configs.{}".format(args.pathogen), \
            fromlist=['']).make_config(args, logger)
        assert type(CONFIG) is dict, logger.error("")
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

    if len(args.metafiles) > 0:
        logger.info("Reading metadata files")
        for f in args.metafiles:
            (tag, list_of_dicts) = read_metafile_to_dictionaries(f)
            dataset.make_metadata_units(tag, list_of_dicts)

    if args.use_entrez_to_improve_data:
        accs = get_all_accessions(dataset)
        list_of_dicts = retrieve_entrez_metadata(accs, CONFIG)
        dataset.make_metadata_units("accession", list_of_dicts)

    if args.metafiles or args.use_entrez_to_improve_data:
        dataset.clean_metadata_units()
        dataset.inject_metadata_into_data()

        dataset.update_units_pre_merge()

    dataset.merge_units()

    dataset.validate_units()

    valid_file = args.outfile
    invalid_file = 'output/invalid.json'
    dataset.write_valid_units(valid_file)
    dataset.write_invalid_units(invalid_file)



if __name__ == "__main__":
    args = parser.parse_args()
    ## LOGGING:
    # https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters
    root_logger = logging.getLogger('')
    root_logger.setLevel(args.loglevel if args.loglevel else logging.INFO)
    root_logger.addHandler(ColorizingStreamHandler())
    logger = logging.getLogger(__name__)
    provision_directories(logger)
    main(args, logger)
