from __future__ import division, print_function
import logging
import os, sys, re
logger = logging.getLogger(__name__)
from spec_mapping import mapping as spec

valid_keys = [v for k in spec for v in spec[k]]
def merge_into(a, b):
    for k, v in b.iteritems():
        a[k] = v

def process_genbank_record(accession, record, config):
    source = [x for x in record.features if x.type == "source"][0].qualifiers
    reference = choose_best_reference(record)
    data = {}
    data["accession"] = accession
    logger.info("Processing entrez seqrecord for {} ({})".format(accession, record.description))
    # other set methods are defined in the config
    for name, fn in config["genbank_setters"].iteritems():
        fn(data, record, source, reference, logger)
    logger.debug("\tDATA: {}".format({k:v for k, v in data.iteritems() if k != "sequence"}))
    return data

def choose_best_reference(record):
    if len(record.annotations["references"]):
        # is there a reference which is not a "Direct Submission"?
        titles = [reference.title for reference in record.annotations["references"]]
        try:
            idx = [i for i, j in enumerate(titles) if j is not None and j != "Direct Submission"][0]
        except IndexError: # fall back to direct submission
            idx = [i for i, j in enumerate(titles) if j is not None][0]
        return record.annotations["references"][idx] # <class 'Bio.SeqFeature.Reference'>
    logger.debug("\tskipping attribution as no suitable reference found")
    return False

### SET METHODS (these become part of the config, and are then passed to process_genbank_record)
###             all methods have the same arguments passed to them
def set_strain_name(data, record, source, reference, logger):
    source = dict(source)
    print(source)
    try:
        if "strain" in source.keys():
            data["strain_name"] = source["strain"][0]
            logger.debug("Setting strain_name to {}".format(source["strain"][0]))
        elif "isolate" in source.keys():
            logger.debug("Setting strain_name to {}".format(source["isolate"][0]))
            data["strain_name"] = source["isolate"][0]
        else:
            raise Exception
    except:
        logger.warn("\tError setting strain_name")

def set_sample_name(data, record, source, reference, logger):
    try:
        data["sample_name"] = source["sample"][0]
    except:
        logger.debug("\tError setting sample_name")

def set_sequence(data, record, source, reference, logger):
    try:
        data["sequence"] = str(record.seq)
    except:
        logger.warn("\tError setting sequence")

def set_sequence_url(data, record, source, reference, logger):
    data["sequence_url"] = "https://www.ncbi.nlm.nih.gov/nuccore/{}".format(data["accession"])

def set_collection_date(data, record, source, reference, logger):
    try:
        data["collection_date"] = source["collection_date"][0]
    except:
        logger.debug("\tError setting collection date")

def set_host_species(data, record, source, reference, logger):
    try:
        data["host_species"] = source["host"][0]
    except:
        logger.debug("\tError setting host")

def set_country(data, record, source, reference, logger):
    try:
        data["country"] = source["country"][0].split(':')[0].strip()
    except:
        logger.debug("\tError setting country")

def set_division(data, record, source, reference, logger):
    try:
        if "division" in source:
            source["division"] = source["division"][0]
        elif "country" in source and ":" in source["country"][0]:
            data["country"] = source["country"][0].split(':')[1].strip()
        else:
            raise(KeyError)
    except:
        logger.debug("\tError setting division")

def set_collecting_lab(data, record, source, reference, logger):
    try:
        data["collecting_lab"] = source["collected_by"][0]
    except:
        logger.debug("\tError setting collecting lab")

def set_genotype(data, record, source, reference, logger):
    try:
        if "genotype" in source:
            data["genotype"] = source["genotype"][0]
        else:
            for note in source['note']:
                if "genotype" in note:
                    if ":" in note:
                        data["genotype"] = note.split(':')[1].strip()
                    else:
                        data["genotype"] = note.split('=')[1].strip()
    except:
        logger.debug("\tError setting genotype")

def set_tissue(data, record, source, reference, logger):
    try:
        data["tissue"] = source["isolation_source"][0]
    except:
        logger.debug("\tError setting tissue")

def set_attribution_title(data, record, source, reference, logger):
    try:
        data["attribution_title"] = reference.title
    except:
        logger.debug("\tError setting attribution_title")

def set_authors(data, record, source, reference, logger):
    try:
        if reference.authors is None: raise ValueError
        first_author = re.match(r'^([^,]*)', reference.authors).group(0)
        data['authors'] = first_author + " et al"
    except:
        logger.debug("\tError setting authors")

def set_attribution_journal(data, record, source, reference, logger):
    try:
        if reference.journal is None: raise ValueError
        data["attribution_journal"] = reference.journal
    except:
        logger.debug("\tError setting attribution_journal")

def set_attribution_url(data, record, source, reference, logger):
    try:
        if reference.pubmed_id is None: raise ValueError
        data["attribution_url"] = "https://www.ncbi.nlm.nih.gov/pubmed/" + reference.pubmed_id
    except:
        logger.debug("\tError setting attribution_url")

def convert_gb_date(self, collection_date):
        '''
        Converts calendar dates between given formats
        '''
        N_fields = len(collection_date.split('-'))
        if N_fields == 1:
            return datetime.datetime.strftime(datetime.datetime.strptime(collection_date,'%Y'), '%Y-XX-XX')
        elif N_fields == 2:
            if collection_date.split('-')[0].isdigit():
                if int(collection_date.split('-')[0]) < 13:
                    return datetime.datetime.strftime(datetime.datetime.strptime(collection_date,'%m-%Y'), '%Y-%m-XX')
                else:
                    return datetime.datetime.strftime(datetime.datetime.strptime(collection_date,'%Y-%m'), '%Y-%m-XX')
            else:
                return datetime.datetime.strftime(datetime.datetime.strptime(collection_date,'%b-%Y'), '%Y-%m-XX')
        elif N_fields == 3:
            if int(collection_date.split('-')[0]) < 32:
                return datetime.datetime.strftime(datetime.datetime.strptime(collection_date,'%d-%b-%Y'), '%Y-%m-%d')
            else:
                return datetime.datetime.strftime(datetime.datetime.strptime(collection_date,'%Y-%m-%d'), '%Y-%m-%d')
