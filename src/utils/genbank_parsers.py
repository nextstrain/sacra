from __future__ import division, print_function
import logging
import os, sys, re
logger = logging.getLogger(__name__)
from spec_mapping import mapping as spec

valid_keys = [v for k in spec for v in spec[k]]
def merge_into(a, b):
    for k, v in b.iteritems():
        a[k] = v

# this is a class so that one can replace a function by subclassing
class GenbankParser(object):
    """docstring for GenbankParser."""

    def __init__(self, record):
        """this does the parsing...."""
        super(GenbankParser, self).__init__()
        self.record = record
        self.source = [x for x in record.features if x.type == "source"][0].qualifiers
        self.reference = self.choose_best_reference()
        self.data = {}
        logger.debug("Processing entrez seqrecord for: " + record.description)

        ## SET DATA
        self.set_accession()
        self.set_strain_name()
        self.set_sample_name()
        self.set_sequence()
        self.set_host_species()
        self.set_collection_date()
        self.set_country()
        self.set_division()
        self.set_collecting_lab()
        self.set_genotype()
        self.set_tissue()
        self.set_sequence_url()

        ## SET ATTRIBUTIONS ##
        if self.reference:
            self.set_authors()
            self.set_attribution_journal()
            self.set_attribution_url()
            self.set_attribution_title()

        logger.debug("\tDATA: {}".format({k:v for k, v in self.data.iteritems() if k != "sequence"}))

    ### CHOOSE REFERENCE FOR ATTRIBUTION ###
    def choose_best_reference(self):
        data = {}
        if len(self.record.annotations["references"]):
            # is there a reference which is not a "Direct Submission"?
            titles = [reference.title for reference in self.record.annotations["references"]]
            try:
                idx = [i for i, j in enumerate(titles) if j is not None and j != "Direct Submission"][0]
            except IndexError: # fall back to direct submission
                idx = [i for i, j in enumerate(titles) if j is not None][0]
            return self.record.annotations["references"][idx] # <class 'Bio.SeqFeature.Reference'>
        logger.debug("\tskipping attribution as no suitable reference found")
        return False

    ### GET METHODS ###
    def get_data(self):
        return self.data

    ### SET METHODS
    def set_accession(self):
        self.data["accession"] = re.match(r'^([^.]*)', self.record.id).group(0).upper()

    def set_sequence_url(self):
        self.data["sequence_url"] = "https://www.ncbi.nlm.nih.gov/nuccore/{}".format(self.data["accession"])

    def set_collection_date(self):
        try:
            self.data["collection_date"] = self.source["collection_date"][0]
        except:
            logger.debug("\tError setting collection date")

    def set_host_species(self):
        try:
            self.data["host_species"] = self.source["host"][0]
        except:
            logger.debug("\tError setting host")

    def set_country(self):
        try:
            self.data["country"] = self.source["country"][0].split(':')[0].strip()
        except:
            logger.debug("\tError setting country")

    def set_division(self):
        try:
            if "division" in self.source:
                self.source["division"] = self.source["division"][0]
            elif "country" in self.source and ":" in self.source["country"][0]:
                self.data["country"] = self.source["country"][0].split(':')[1].strip()
            else:
                raise(KeyError)
        except:
            logger.debug("\tError setting division")

    def set_collecting_lab(self):
        try:
            self.data["collecting_lab"] = self.source["collected_by"][0]
        except:
            logger.debug("\tError setting collecting lab")

    def set_genotype(self):
        try:
            if "genotype" in self.source:
                self.data["genotype"] = self.source["genotype"][0]
            else:
                for note in self.source['note']:
                    if "genotype" in note:
                        if ":" in note:
                            self.data["genotype"] = note.split(':')[1].strip()
                        else:
                            self.data["genotype"] = note.split('=')[1].strip()
        except:
            logger.debug("\tError setting genotype")

    def set_tissue(self):
        try:
            self.data["tissue"] = self.source["isolation_source"][0]
        except:
            logger.debug("\tError setting tissue")

    def set_strain_name(self):
        try:
            self.data["strain_name"] = self.source["strain"][0]
        except:
            logger.warn("\tError setting strain_name")

    def set_sample_name(self):
        try:
            self.data["sample_name"] = self.source["sample"][0]
        except:
            logger.debug("\tError setting sample_name")

    def set_sequence(self):
        try:
            self.data["sequence"] = str(self.record.seq)
        except:
            logger.warn("\tError setting sequence")

    def set_attribution_title(self):
        try:
            self.data["attribution_title"] = self.reference.title
        except:
            logger.debug("\tError setting attribution_title")

    def set_authors(self):
        try:
            if self.reference.authors is None: raise ValueError
            first_author = re.match(r'^([^,]*)', self.reference.authors).group(0)
            self.data['authors'] = first_author + " et al"
        except:
            logger.debug("\tError setting authors")

    def set_attribution_journal(self):
        try:
            if self.reference.journal is None: raise ValueError
            self.data["attribution_journal"] = self.reference.journal
        except:
            logger.debug("\tError setting attribution_journal")

    def set_attribution_url(self):
        try:
            if self.reference.pubmed_id is None: raise ValueError
            self.data["attribution_url"] = "https://www.ncbi.nlm.nih.gov/pubmed/" + self.reference.pubmed_id
        except:
            logger.debug("\tError setting attribution_url")
