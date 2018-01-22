def get_counter():
    count = 0
    while True:
        yield count
        count += 1

counter = get_counter()

def create_sample_name(doc, *args):
    '''
    the input file may not have a "sample_name" field, so it should be created
    '''
    if 'sample_name' not in doc:
        doc['sample_name'] = "sample_{}".format(counter.next())
