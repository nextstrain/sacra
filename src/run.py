from __future__ import division, print_function
from dataset import Dataset
import logging
import argparse
import sys
sys.path.append('')
import config
from utils.colorLogging import ColorizingStreamHandler

parser = argparse.ArgumentParser(description="Cleaning & combining of genomic & titer data")
parser.add_argument("--debug", action="store_const", dest="loglevel", const=logging.DEBUG, help="Enable debugging logging")
parser.add_argument("--files", default=[], type=str, nargs='*')
parser.add_argument("--pathogen", default="mumps", type=str)
parser.add_argument("--accession_list", default=[], type=str, nargs='*')
parser.add_argument("--outfile", default="output/test_output.json")

group = parser.add_argument_group('entrez')
group.add_argument("--skip_entrez", action="store_true")


if __name__=="__main__":
    args = parser.parse_args()

    ## L O G G I N G
    # https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters
    root_logger = logging.getLogger('')
    root_logger.setLevel(args.loglevel if args.loglevel else logging.INFO)
    root_logger.addHandler(ColorizingStreamHandler())

    # Initialize
    CONFIG = config.produce_config_dictionary(args.pathogen)
    dataset = Dataset(args.pathogen, CONFIG)
    # Read data from files
    for f in args.files:
        dataset.read_to_clusters(f)
    # Update clusters with data from entrez
    if not args.skip_entrez:
        if args.accession_list:
            # "read" accession list for building cluster from entrez
            dataset.accessions_to_clusters(args.accession_list)
        # Update existing from entrez
        accessions = dataset.get_all_accessions()
        dataset.download_entrez_data(accessions)
    # Clean clusters
    dataset.clean_clusters()
    # Write to JSON
    dataset.write_to_json(args.outfile)
