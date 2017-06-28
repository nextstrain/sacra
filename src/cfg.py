# TODO, This needs to be reformatted to be more user friendly
from cleaning_functions import *
viruses = ['seasonal_flu']
datatypes = ['titer', 'sequence', 'virus']

virus_clean = []

sequence_clean = [ fix_accession, fix_sequence, fix_locus, fix_strain, fix_isolate_id, fix_passage, fix_submitting_lab ]

sources = { 'sequence' : ['gisaid'],
            'titer' : ['crick', 'cdc'] }

subtypes = { 'seasonal_flu': ['h3n2', 'h1n1pdm', 'vic', 'yam'] }
