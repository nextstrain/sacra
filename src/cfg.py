# TODO, This needs to be reformatted to be more user friendly
from cleaning_functions import *
viruses = ['seasonal_flu']
datatypes = ['titer', 'sequence', 'virus']

virus_clean = [ fix_casing ]


sequence_clean = [ fix_casing ]

sources = { 'sequence' : ['gisaid'],
            'titer' : ['crick', 'cdc'] }

subtypes = { 'seasonal_flu': ['h3n2', 'h1n1pdm', 'vic', 'yam'] }
