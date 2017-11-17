def fix_locus(doc, key, remove, *args):
    if 'locus' in doc and doc['locus'] is not None:
        doc['locus'] = doc['locus'].lower()
    else:
        remove.append(key)
