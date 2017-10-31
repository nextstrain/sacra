def fix_accession(doc, key, remove, *args):
    '''
    fix errors that can arise with accession field
    '''
    if 'accession' in doc and doc['accession'] is not None:
        doc['accession'] = doc['accession'].encode('ascii', 'replace')
        doc['accession'] = doc['accession'].lower()
        if doc['accession'].startswith('epi'):
            doc['accession'] = doc['accession'][2:]
