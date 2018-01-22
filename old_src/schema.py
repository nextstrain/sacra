# This could be made a class with methods...
# 1 idea: the schema class holds an instance of data, i.e.
#        a parsed doc (e.g. fasta file) is turned into a schema instance
#        by using "set" methods which are the "reshape" methods in dataset
#       and then this could be merged with the main schema instance using merge
#       methods defined in this class... this would allow a single, consistent &
#       well thought out merge algorithm

tables = ["strains", "samples", "sequences", "attributions"]; # dbinfo ?

tables_primary_keys = {
    # "dbinfo": "pathogen",
    "strains": "strain_id",
    "samples": "sample_id",
    "sequences": "sequence_id",
    "attributions": "attribution_id"
}

join_char = '|'

make_primary_key = {
    "strain_id": lambda x: x["strain_name"],
    "sample_id": lambda x: join_char.join([x["strain_name"], x["sample_name"]]),
    "sequence_id": lambda x: join_char.join([x["strain_name"], x["sample_name"], x["sequence_name"]]),
    "attribution_id": lambda x: "{}_{}_{}".format( # why does attribution_id use _ not | ?!?
        x["authors"].split(" ")[0].lower(),
        x["attribution_date"].split("-")[0],
        x["attribution_title"].split(" ")[0].lower()
    )
}

fields = {  'dbinfo' : ['pathogen'],
            'strains' : ['strain_id', 'strain_name', 'strain_owner',
                         'host_species', 'host_age', 'host_sex',
                         'symptom_onset_date', 'symptoms',
                         'pregnancy_status', 'pregnancy_week',
                         'microcephaly_status', 'usvi_doh_patient_id'],
            'samples' : ['sample_id', 'sample_name', 'sample_owner',
                         'collection_date', 'country', 'division', 'subdivision',
                         'gps', 'collecting_lab', 'passage', 'tissue', 'ct',
                         'usvi_doh_sample_id', 'sample_strain_name'],
            'sequences' : ['sequence_id', 'sequence_name',
                           'sequence_sample_name', 'sequence_owner', 'locus',
                           'sequence_type', 'sequencing_lab', 'sharing',
                           'sequence_url', 'attribution', 'sequence'],
            'attributions' : ['attribution_id', 'attribution_owner',
                              'attribution_source', 'publication_status',
                              'attribution_date', 'attribution_title',
                              'attribution_journal', 'attribution_url',
                              'authors', 'pubmed_id']}
