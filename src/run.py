from __future__ import division, print_function
from dataset import Dataset
import logging
import argparse
import sys
sys.path.append('')
import config
from utils.colorLogging import ColorizingStreamHandler


from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph.output import GraphvizOutput


parser = argparse.ArgumentParser(description="Cleaning & combining of genomic & titer data")
parser.add_argument("--debug", action="store_const", dest="loglevel", const=logging.DEBUG, help="Enable debugging logging")
parser.add_argument("--files", default=[], type=str, nargs='*', help="file types: text (list of accessions), FASTA, (to do) FASTA + CSV, (to do) JSON")
parser.add_argument("--pathogen", required=True, type=str, help="This sets the config file")
parser.add_argument("--accession_list", default=[], type=str, nargs='*', help="list of strings to query genbank with")
parser.add_argument("--outfile", default="output/test_output.json")
parser.add_argument("--visualize_call_graph", action="store_true", default=False, help="draw a graph of calls being made")
parser.add_argument("--call_graph_fname", default="output/graphviz_test.png", help="filename for call graph")

group = parser.add_argument_group('entrez')
group.add_argument("--skip_entrez", action="store_true", help="Query genbank for all accessions to help clean / correct metadata data")


if __name__=="__main__":
    args = parser.parse_args()

    ## L O G G I N G
    # https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters
    root_logger = logging.getLogger('')
    root_logger.setLevel(args.loglevel if args.loglevel else logging.INFO)
    root_logger.addHandler(ColorizingStreamHandler())
    logger = logging.getLogger(__name__)

    if args.visualize_call_graph:
        graphviz = GraphvizOutput()
        graphviz.output_file = args.call_graph_fname

        c = Config(groups=True)
        with PyCallGraph(config=c, output=graphviz):
            try:
                CONFIG = __import__("configs.{}".format(args.pathogen), fromlist=['']).config
            except ImportError:
                logger.critical("Could not load config! File configs/{}.py must exist!".format(args.pathogen)); sys.exit(2)
            except AttributeError:
                logger.critical("Config file configs/{}.py must define a \"config\" dictionary.".format(args.pathogen)); sys.exit(2)
            # Initialize Dataset class
            dataset = Dataset(CONFIG)
            # Read data from files
            for f in args.files:
                dataset.read_to_clusters(f)
            # ditto for accessions if provided as strings on the command line
            if args.accession_list:
                dataset.download_entrez_data(args.accession_list, make_clusters = True)
            # Download additional entrez data which the cleaning functions make make use of
            if not args.skip_entrez:
                logger.info("Fetching entrez data for all available accessions to aid in cleaning the data")
                dataset.download_entrez_data(dataset.get_all_accessions(), make_clusters = False)
            # Clean clusters
            dataset.clean_clusters()
            # Write to JSON
            dataset.write_to_json(args.outfile)
    else:
        try:
            CONFIG = __import__("configs.{}".format(args.pathogen), fromlist=['']).config
        except ImportError:
            logger.critical("Could not load config! File configs/{}.py must exist!".format(args.pathogen)); sys.exit(2)
        except AttributeError:
            logger.critical("Config file configs/{}.py must define a \"config\" dictionary.".format(args.pathogen)); sys.exit(2)
        # Initialize Dataset class
        dataset = Dataset(CONFIG)
        # Read data from files
        for f in args.files:
            dataset.read_to_clusters(f)
        # ditto for accessions if provided as strings on the command line
        if args.accession_list:
            dataset.download_entrez_data(args.accession_list, make_clusters = True)
        # Download additional entrez data which the cleaning functions make make use of
        if not args.skip_entrez:
            logger.info("Fetching entrez data for all available accessions to aid in cleaning the data")
            dataset.download_entrez_data(dataset.get_all_accessions(), make_clusters = False)
        # Clean clusters
        dataset.clean_clusters()
        # Write to JSON
        dataset.write_to_json(args.outfile)
