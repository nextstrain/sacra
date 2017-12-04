def get_counter():
    count = 0
    while True:
        yield count
        count += 1

counter = get_counter()


def create_sequence_name(doc, *args):
    '''
    the fasta file may not have a "sequence_name" field, so it should be created
    '''
    count = 0
    if 'sequence_name' not in doc:
        doc['sequence_name'] = "seq_.{}".format(counter.next())
