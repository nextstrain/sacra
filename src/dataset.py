from __future__ import division, print_function
import logging
import json
import os, sys
from cluster import Cluster
logger = logging.getLogger(__name__)
from entrez import query_genbank
from utils.genbank_parsers import process_genbank_record

flatten = lambda l: [item for sublist in l for item in sublist]

class Dataset:

    # Initializer
    def __init__(self, CONFIG):
        self.CONFIG = CONFIG
        self.clusters = []
        self.genbank_data = {}

    # File handling
    def read_to_clusters(self, f):
        logger.info("Initializing sacra parse of files ---")
        ftype = self.infer_ftype(f)
        if ftype == "accessions":
            accessions = self.get_accessions_from_file(f)
            self.download_entrez_data(accessions, make_clusters=True)
        elif ftype == "fasta":
            unmerged_clusters = self.read_fasta_to_clusters(f)
            self.merge_clusters_into_state(unmerged_clusters)
        else:
            logger.error("Unknown input filetype for {}. Fatal.".format(f))
            sys.exit(2)


    def read_fasta_to_clusters(self, infile):
        from Bio import SeqIO
        '''
        Take a fasta file and a list of information contained in its headers
        and build a dataset object from it.

        # TODO: This should return a docs structure
        # (list of docs dicts) instead of its current behavior
        '''
        logger.info('Reading in FASTA from %s.' % (infile))

        clusters = []
        # Read the fasta
        with open(infile, "rU") as f:

            for record in SeqIO.parse(f, "fasta"):
                data = {}
                head = record.description.replace(" ","").split('|')
                for i in range(len(self.CONFIG["fasta_headers"])):
                    data[self.CONFIG["fasta_headers"][i]] = head[i]
                    data['sequence'] = str(record.seq)
                logger.debug("Processing this header: {}".format(data))
                clus = Cluster(self.CONFIG, data)
                att = Cluster(self.CONFIG, data, cluster_type="attribution")

                # link the attribute id to each sequence in the cluster
                if att.is_valid() and clus.is_valid():
                    for s in clus.sequences:
                        s.attribution_id = att.get_all_units()[0].attribution_id
                if clus.is_valid(): clusters.append(clus)
                if att.is_valid(): clusters.append(att)
        return clusters

    def get_accessions_from_file(self, fname):
        accessions = []
        try:
            with open(fname, "r") as f:
                for line in f:
                    accessions.append(line.strip())
        except IOError:
            logger.error("File {} could not be read. Skipping.".format(fname))
        return accessions

    # Random utils
    def infer_ftype(self, fname):
        if fname.endswith(".fasta"):
            return "fasta"
        if fname.endswith(".txt"):
            return "accessions"
        # elif (fname.endswith(".json")):
        #     return "json"

    def download_entrez_data(self, accessions, make_clusters = False):
        ## don't fetch data that's already fetched!
        new_accs = [x for x in accessions if x not in self.genbank_data.keys()]
        logger.info("Fetching {} additional genbank entries".format(len(new_accs)))
        if len(new_accs):
            new_data = query_genbank(new_accs)
            for k, v in new_data.iteritems():
                self.genbank_data[k] = v

        if make_clusters:
            data_dicts = [process_genbank_record(accession, record, self.CONFIG) for \
                accession, record in self.genbank_data.iteritems() if accession in accessions]
            unmerged_clusters = flatten(
                [[Cluster(self.CONFIG, d), Cluster(self.CONFIG, d, cluster_type="attribution")] for d in data_dicts]
            )
            self.merge_clusters_into_state(unmerged_clusters)

    def get_all_accessions(self):
        '''
        Read through all clusters to generate accession list for
        batch submission to entrez
        '''
        flatten = lambda l: [item for sublist in l for item in sublist]
        accs = flatten([c.get_all_accessions() for c in self.clusters])
        logger.debug("These are the accessions: {}".format(accs))
        return accs

    # Merging and cleaning
    def merge_clusters_into_state(self, clusters):
        logger.debug("simply setting state to clusters!")
        self.clusters.extend(clusters)

    def clean_clusters(self):
        logger.info("Cleaning clusters (move / fix / create / drop)")
        [c.clean() for c in self.clusters]

    # Output
    def write_to_json(self, filename):
        logger.info("writing to JSON: {}".format(filename))
        data = {"strains": [], "samples": [], "sequences": [], "attributions": []}
        data["dbinfo"] = {"pathogen": self.CONFIG["pathogen"]}
        for c in self.clusters:
            for n in ["strains", "samples", "sequences", "attributions"]:
                if hasattr(c, n): data[n].extend([x.get_data() for x in getattr(c, n)])
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, ensure_ascii=False)
