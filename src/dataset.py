from __future__ import division, print_function
import logging
import json
from cluster import Cluster
logger = logging.getLogger(__name__)
from entrez import query_genbank

class Dataset:


    # Initializer
    def __init__(self, pathogen, config):
        self.pathogen = pathogen
        self.config = config
        self.clusters = []

    # File handling
    def read_to_clusters(self, f):
        logger.info("Initializing sacra parse of files ---")
        #ftype = self.determine_filetype(f)
        ftype = "fasta"
        if ftype == "fasta":
            # TODO: should this be saved to a variable for readability?
            unmerged_clusters = self.read_fasta_to_clusters(f)
            self.merge_clusters_into_state(unmerged_clusters)


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
                for i in range(len(self.config["fasta_headers"])):
                    data[self.config["fasta_headers"][i]] = head[i]
                    data['sequence'] = str(record.seq)
                logger.debug("Processing this header: {}".format(data))
                C = Cluster(data)
                Delta = Cluster(data, cluster_type="attribution")
                if Delta:
                    clusters.extend([C,Delta])
                else:
                    clusters.append(C)
        return clusters

    # Entrez handling
    def accessions_to_clusters(self, accession_list):
        logger.info("Initializing construction of clusters from ---")

    def download_entrez_data(self, accessions):
        self.genbank_data = query_genbank(accessions)

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
        [c.clean() for c in self.clusters]

    # Output
    def write_to_json(self, filename):
        logger.info("writing to JSON: {}".format(filename))
        data = {}
        data["dbinfo"] = {"pathogen": self.pathogen}
        data["strains"] = [y.get_data() for x in self.clusters for y in x.strains]
        data["samples"] = [y.get_data() for x in self.clusters for y in x.samples]
        data["sequences"] = [y.get_data() for x in self.clusters for y in x.sequences]
        data["attributions"] = [y.get_data() for x in self.clusters for y in x.attributions]

        with open(filename, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, ensure_ascii=False)
