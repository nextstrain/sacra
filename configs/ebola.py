from __future__ import division, print_function
import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.file_readers import make_dict_from_file
import src.utils.fix_functions as fix_functions

### modified functions ###
name_fix_dict = make_dict_from_file("source-data/ebola_strain_name_fix.tsv")
date_fix_dict = make_dict_from_file("source-data/ebola_date_fix.tsv")

def fix_strain_name(obj, name, logger):
    try:
        name = 'V' + str(int(name))
    except:
        pass
    return name

def make_config(args, logger):
    """ make the function - you can use the args to customise it. Try to minimise the customisation! """
## initialise with default config
    config = default_config
    config["pathogen"] = "ebola"
    if args.overwrite_fasta_header:
        if args.overwrite_fasta_header == "fauna":
            config["fasta_headers"] = [
                'strain_name',
                'virus',
                'accession',
                'collection_date',
                'unused', # region
                'country',
                'division',
                'location',
                'unused', # genbank field
                'unused', # genome
                'authors',
                'accession_url',
                'publication_name',
                'journal',
                'attribution_url'
            ]
        elif args.overwrite_fasta_header == "sacra_rebuild":
            config["fasta_headers"] = [
                'accession',
                'authors',
                'attribution_journal',
                'locus',
                'unused',
                'attribution_url',
                'attribution_source',
                'strain_name',
                'unused',
                'attribution_title',
                'sequence_url',
                'pathogen',
                'collection_date',
                'country',
                'division',
                'host_species',
                'number_sequences',
                'region']
        else:
            logger.critical("Unknown FASTA header format demanded: \"{}\"".format(args.overwrite_fasta_header)); sys.exit(2)
    else:
        config["fasta_headers"] = [
            'strain_name',
            'virus',
            'accession',
            'collection_date',
            'country',
            'division',
            'muv_genotype',
            'host',
            'authors',
            'publication_name',
            'journal',
            'attribution_url',
            'accession_url'
        ]
    config["fix_functions"]["strain_name"] = fix_strain_name
    config["fix_functions"]["authors"] = fix_authors
    config["fix_lookups"]["strain_name_to_location"] = "source-data/ebola_location_fix.tsv"
    config["fix_lookups"]["strain_name_to_date"] = "source-data/ebola_date_fix.tsv"
    return config
