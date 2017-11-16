def fix_sequence_name(doc, key, remove, *args):
    '''
    fix errors that can arise with sequence_name field
    '''
    if 'sequence_name' in doc and doc['sequence_name'] is not None:
        doc['sequence_name'] = doc['sequence_name'].encode('ascii', 'replace')
        doc['sequence_name'] = doc['sequence_name'].lower()
        if doc['sequence_name'].startswith('epi'):
            doc['sequence_name'] = doc['sequence_name'][2:]
