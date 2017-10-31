def fix_sequence(doc, key, remove, *args):
    if 'sequence' in doc and doc['sequence'] is not None:
        doc['sequence'] = doc['sequence'].upper()
    else:
        remove.append(key)
