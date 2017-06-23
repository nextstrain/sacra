import os, time, datetime, csv, sys, json
from Bio import SeqIO

class Dataset:
    '''
    Defines 'Dataset' class, containing procedures for uploading documents from un-cleaned FASTA files
    and turning them into rich JSONs that can be:
        - Uploaded to the fauna database
        - imported directly by augur (does not take JSONs at this time, instead needs FASTAs)

    Each instance of a Dataset contains:
        1. metadata: list of high level information that governs how the data contained in the Dataset
        are treated by Dataset cleaning functions (TODO: Make these in external scripts as a library of
        functions that can be imported by the Dataset), as well as the exact location in the fauna
        database where the dataset should be stored (TODO: specify in a markdown file somewhere exactly
        what the fauna db should look like).

        ex. [FIGURE OUT WHAT THIS WILL LOOK LIKE]

        2. dataset: A list of dictionaries, each one identical in architecture representing 'documents'
        that are contained within the Dataset. These dictionaries represent both lower-level metadata,
        as well as the key information (sequence, titer, etc) that is being stored/run in augur.

        ex. [ {date: 2012-06-11, location: Idaho, sequence: GATTACA}, {date: 2016-06-16, location: Oregon, sequence: CAGGGCCTCCA}, {date: 1985-02-22, location: Brazil, sequence: BANANA} ]
    '''
    def __init__(self, datatype, virus, **kwargs):
        print 'kwargs: '
        print kwargs
        # Wrappers for data, described in class description
        self.metadata = {'datatype': datatype, 'virus': virus}
        self.dataset = []

        if datatype == 'sequence':
            self.read_fasta(**kwargs)
            seed = { header : None for header in self.fasta_headers }
            seed['sequence'] = None
            self.dataset.append(seed)


    def read_fasta(self, infile, source, path, **kwargs):
        '''
        Take a fasta file and a list of information contained in its headers
        and build a dataset object from it.
        '''
        ######### Update here with new sources, as they are added
        if source.lower() == 'gisaid':
            self.fasta_headers = ['accession', 'strain', 'isolate_id', 'locus', 'passage', 'submitting_lab']
        else:
            print 'Unable to parse fasta from source %s' % (source)
            sys.exit()
        #########

        out = []

        # Read the fasta
        with open(path + infile, "rU") as f:

            for record in SeqIO.parse(f, "fasta"):
                data = {}
                head = record.description.replace(" ","").split('|')
                for i in range(len(self.fasta_headers)):
                    data[self.fasta_headers[i]] = head[i]
                    data['sequence'] = str(record.seq)

        # Merge the formatted dictionaries to self.dataset()
        for doc in out:
            self.merge(doc)
        # TODO: Find a way to resolve index collisions
        self.dataset.append(out)

    def read_xml(self):
        '''
        Read an xml file to a metadata dataset
        '''
        return

    def merge(self, data):
        '''
        Make sure all new entries to the dataset have matching keys
        '''
        match = True
        indices = data.keys()
        for doc in indices:
            for key in data[doc]:
                if key not in self.dataset[0].keys():
                    print('Error adding ' + key + ' to dataset, keys don\'t match.')
                    match = False

        if match:
            self.dataset.append(data)

    def clean(self):
        import CONFIG as c
        if self.metadata['dtype'] == 'virus':
            fxns = c.virus_clean
        elif self.metadata['dtype'] == 'sequence':
            fxns = c.sequence_clean
        elif self.metadata['dtype'] == 'titer':
            fxns = c.titer_clean

        for fxn in fxns:
            #TODO THIS
            pass


    def write(self, out_type, out_file):
        # remove seed
        temp = self.dataset[-1]
        self.dataset[0] = temp
        self.dataset.pop()

        out = {}
        for key in self.metadata.keys():
            out[key] = self.metadata[key]
        out['data'] = self.dataset


        if out_type == 'json':
            with open(out_file, 'w+') as f:
                json.dump(out, f, indent=1)
