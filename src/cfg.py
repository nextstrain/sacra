# TODO, This needs to be reformatted to be more user friendly
viruses = ['seasonal_flu']
datatypes = ['titer', 'sequence', 'virus']

virus_clean = [ ( 'fix_casign', None ),
                ( 'fix_age', None ),
                ( 'format_date', None ),
                ( 'format_country', None ),
                ( 'format_place', None ),
                ( 'format_region', None ),
                ( 'determine_latitide_longitude', None ) ]


sequence_clean = [  ( 'format_date', None ),
                    ( 'format_passage', ['passage', 'passage_category'] ),
                    ( 'format_passage', ['virus_strain_passage', 'virus_strain_passage_category'] ),
                    ( 'format_passage', ['serum_antigen_passage', 'serum_antigen_passage_category'] ),
                    ( 'fix_casing', None )  ]

sources = { 'sequence' : ['gisaid'],
            'titer' : ['crick', 'cdc'] }

subtypes = { 'seasonal_flu': ['h3n2', 'h1n1pdm', 'vic', 'yam'] }
