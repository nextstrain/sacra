# TODO, This needs to be reformatted to be more user friendly
from old_cleaning_functions import *

### Acceptable parameters ###
viruses = [ 'seasonal_flu' ]
subtypes = { 'seasonal_flu': [ 'h3n2', 'h1n1pdm', 'vic', 'yam' ] }
datatypes = [ 'titer', 'sequence', 'virus' ]
filetypes = [ 'fasta' ]

### Cleaning functions for different datatypes ###
# Functions should be defined in cleaning_functions.py
virus_clean = []
sequence_clean = [ fix_accession, fix_sequence, fix_locus, fix_strain, remove_isolate_id, fix_passage, fix_submitting_lab, fix_age, determine_passage_category ]

### Mappings used by sacra ###
# Lists sources from which different datatypes come from
sources = { 'sequence' : [ 'gisaid', 'fauna', 'vipr' ],
            'titer' : [ 'crick', 'cdc' ] }
# When running reshape, figure out which fields belong in which table
# Lifted from schema/schema_zika.json
table_to_fields = { 'dbinfo' : ['pathogen'],
                    'strains' : ['strain_id', 'strain_name', 'strain_owner',
                                 'host_species', 'host_age', 'host_sex',
                                 'symptom_onset_date', 'symptoms',
                                 'pregnancy_status', 'pregnancy_week',
                                 'microcephaly_status', 'usvi_doh_patient_id'],
                    'samples' : ['sample_id', 'sample_name', 'sample_owner',
                                 'collection_date', 'country', 'division', 'subdivision',
                                 'gps', 'collecting_lab', 'passage', 'tissue', 'ct',
                                 'usvi_doh_sample_id'],
                    'sequences' : ['sequence_id', 'strain_name', 'strain_sample',
                                   'sequence_accession', 'sequence_owner', 'sequence_locus',
                                   'sequence_type', 'sequencing_lab', 'sharing',
                                   'sequence_url', 'attribution', 'sequence'],
                    'attributions' : ['attribution_id', 'attribution_owner',
                                      'attribution_source', 'publication_status',
                                      'attribution_date', 'attribution_title',
                                      'attribution_journal', 'attribution_url',
                                      'authors', 'pubmed_id']}
##### strain_sample from https://github.com/nextstrain/sacra/blob/schema/schema/schema_zika.json#L100
# For each sequence source, the default order of fields in the fasta header
fasta_headers = { 'gisaid' : [ 'accession', 'strain', 'isolate_id', 'locus', 'passage', 'submitting_lab' ],
                  'fauna' : [ 'strain', 'virus', 'accession', 'collection_date', 'region', 'country', 'division', 'location', 'passage', 'source', 'age' ],
                  'vipr': [ 'accession', 'strain', 'locus', 'date', 'host', 'country', 'subtype', 'virus' ] }

metadata_fields = set( [ 'isolate_id', 'subtype', 'submitting_lab', 'passage_history', 'location', 'collection_date' ] )
required_fields = { 'sequence' : { 'strain', 'date', 'accession', 'source', 'locus', 'sequence', 'isolate_id' } }
optional_fields = { 'sequence': { 'strain', 'date', 'passage_category', 'source', 'submitting_lab',
                                  'accession', 'host_age', 'locus', 'sequence', 'isolate_id' } }


### Mappings used by cleaning functions ###
# Used in strain name formatting
strain_fix_fname = { 'seasonal_flu' : 'source-data/flu_strain_name_fix.tsv' }
label_fix_fname = { 'seasonal_flu' : 'source-data/flu_fix_location_label.tsv' }
