from __future__ import division, print_function
import utils.genbank_parsers as gbp
import utils.fix_functions as fix
# import utils.create_functions as create

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
    },
    "fix_lookups": {
        "strain_name_to_strain_name": None,
        "strain_name_to_location": None,
        "strain_name_to_date": None,
        "country_to_region": "source-data/geo_regions.tsv",
        "geo_synonyms": "source-data/geo_synonyms.tsv"
    },
    'lookups' : {}, # TODO: move fix_lookups into here and process in a single place.
    "fix_functions": {
        "strain_name": fix.strain_name,
        "collection_date": fix.collection_date,
        "attribution_id": fix.attribution_id,
        "country": fix.country,
        "division": fix.division,
        "location": fix.location,
        "region": fix.region,
        "sample_name": fix.sample_name,
        "passage": fix.passage
    },
    # TODO: Make this a real minimal default config
    "mapping" : {
        'dbinfo' : ['pathogen'],
        'strain' : [
            'strain_id',
            'strain_name',
            'host_species',
            'host_age',
            'host_sex',
            'genotype'
        ],
        'sample' : [
            'sample_id',
            'sample_name',
            'sample_owner',
            'collection_date',
            'country',
            'division',
            'subdivision',
            'region',
            'gps',
            'collecting_lab',
            'strain_id',
            'passage'
        ],
        'sequence' : [
            'sequence_id',
            'accession',
            'sequence_sample_name',
            'sequence_owner',
            'locus',
            'sequence_type',
            'sequencing_lab',
            'sharing',
            'sequence_url',
            'attribution_id',
            'sequence',
            'sample_id',
            'location',
            'attribution_id'
            'region'
        ],
        'attribution' : [
            'attribution_id',
            'attribution_owner',
            'attribution_source',
            'publication_status',
            'attribution_date',
            'attribution_title',
            'attribution_journal',
            'attribution_url',
            'authors',
            'pubmed_id'
        ]
    },
    'custom_fields': {}
}


common_fasta_headers = {
    ####                1st             2nd         3rd             4th             5th             6th                 7th             8th         9th         10th                11th
    'gisaid' : ['sequence_name', 'strain_name', 'sample_name',  'locus',            'passage',  'sequencing_lab' ],
    'fauna'  : ['strain',        'pathogen',    'sequence_name','collection_date',  'region',   'country',          'division',     'location', 'passage',      'source',           'age' ],
    'vipr'   : ['sequence_name', 'strain',      'locus',        'date',             'host',     'country',          'subtype',      'pathogen' ]
}
