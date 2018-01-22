import logging
logger = logging.getLogger(__name__)

# TODO: current fasta headers field is specific to mumps, will need to be updated

fasta_headers = { 'gisaid' : [ 'sequence_name', 'strain_name', 'sample_name', 'locus', 'passage', 'sequencing_lab' ],
                  'fauna' : [ 'strain', 'pathogen', 'sequence_name', 'collection_date', 'region', 'country', 'division', 'location', 'passage', 'source', 'age' ],
                  'vipr': [ 'sequence_name', 'strain', 'locus', 'date', 'host', 'country', 'subtype', 'pathogen' ],
                  'mumps' : [ 'strain_name', 'virus', 'accession', 'collection_date', 'country', 'division', 'muv_genotype', 'host', 'authors', 'publication_name', 'journal', 'attribution_url', 'accession_url' ]
                  }

def produce_config_dictionary(pathogen):
    logger.info("Constructing config dictionary")
    config = {}
    config["fasta_headers"] = fasta_headers[pathogen]
    return config
