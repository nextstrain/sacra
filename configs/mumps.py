from __future__ import division, print_function
import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.file_readers import make_dict_from_file
import src.utils.fix_functions as fix_functions

### modified functions ###
name_fix_dict = make_dict_from_file("source-data/mumps_strain_name_fix.tsv")
date_fix_dict = make_dict_from_file("source-data/mumps_date_fix.tsv")

def fix_strain_name(obj, name, logger):
    original_name = name
    if name in name_fix_dict:
        name = name_fix_dict[name]
    name = name.replace('MuV/', '').replace('MuVi/', '').replace('MuVs/','')
    name = re.sub(r'[_ ]?\[([A-Z])\]$', r'/\1', name)
    name = re.sub(r'\(([A-Z])\)$', r'/\1', name)
    name = re.sub(r'_([A-Z])_$', r'/\1', name)
    name = re.sub(r'[ ;]', r'_', name)
    name = re.sub(r'//', r'/', name)
    if name in name_fix_dict:
        name = name_fix_dict[name]
    if name is not original_name:
        logger.debug("Changed strain name from {} to {}".format(original_name, name))
    return name

def country(sample, value, logger):
    general_location_fix(sample, "country", geo_synonyms, value, logger)

def division(sample, value, logger):
    general_location_fix(sample, "division", geo_synonyms, value, logger)


def make_config(args, logger):
    """ make the function - you can use the args to customise it. Try to minimise the customisation! """
## initialise with default config
    config = default_config
    config["pathogen"] = "mumps"
    if args.overwrite_fasta_header:
        if args.overwrite_fasta_header == "alt1":
            # ['BCCDC75', 'MuVs/No_designation_vaccine_related/A', '2017-02-28', 'human', 'canada', 'british_columbia', 'A']
            config["fasta_headers"] = [
                "accession",
                'strain_name',
                'collection_date',
                'host',
                'country',
                'division',
                'muv_genotype'
            ]
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
    config["fix_lookups"]["strain_name_to_location"] = "source-data/mumps_location_fix.tsv"
    config["fix_lookups"]["strain_name_to_date"] = "source-data/mumps_date_fix.tsv"
    return config
