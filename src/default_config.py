from __future__ import division, print_function
import utils.genbank_parsers as gbp

"""
This file sets up the default config


"""

default_config = {
    "pathogen": False, # this forces the config to be user specified, as False won't work...
    "fasta_headers": False, # must define in user config
    "genbank_setters": {
        # see src/utils/genbank_parsers to understand these functions
        "set_strain_name": gbp.set_strain_name,
        "set_sample_name": gbp.set_sample_name,
        "set_sequence": gbp.set_sequence,
        "set_sequence_url": gbp.set_sequence_url,
        "set_collection_date": gbp.set_collection_date,
        "set_host_species": gbp.set_host_species,
        "set_country": gbp.set_country,
        "set_division": gbp.set_division,
        "set_collecting_lab": gbp.set_collecting_lab,
        "set_genotype": gbp.set_genotype,
        "set_tissue": gbp.set_tissue,
        "set_attribution_title": gbp.set_attribution_title,
        "set_authors": gbp.set_authors,
        "set_attribution_journal": gbp.set_attribution_journal,
        "set_attribution_url": gbp.set_attribution_url
    }
}


common_fasta_headers = {
    ####                1st             2nd         3rd             4th             5th             6th                 7th             8th         9th         10th                11th
    'gisaid' : ['sequence_name', 'strain_name', 'sample_name',  'locus',            'passage',  'sequencing_lab' ],
    'fauna'  : ['strain',        'pathogen',    'sequence_name','collection_date',  'region',   'country',          'division',     'location', 'passage',      'source',           'age' ],
    'vipr'   : ['sequence_name', 'strain',      'locus',        'date',             'host',     'country',          'subtype',      'pathogen' ]
}
