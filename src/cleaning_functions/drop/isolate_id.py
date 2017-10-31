def drop_isolate_id(doc, key, remove, *args):
    if 'isolate_id' in doc:
        doc.pop('isolate_id', None)
