import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.misc import make_dict_from_file

### modified functions ###
name_fix_dict = make_dict_from_file("source-data/mumps_strain_name_fix.tsv")

def fix_strain_name(name, logger):
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

## initialise with default config
config = default_config
config["pathogen"] = "mumps"
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
