import sys
sys.path.append("")
from src.default_config import default_config, common_fasta_headers

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
