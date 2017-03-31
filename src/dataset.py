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
    def __init__(self, db, virus, subtype=None):
        # Wrappers for data, described in class description
        self.metadata = {'db': db, 'virus': virus, 'subtype': subtype}
        self.dataset = []

        # Log files to cut down on verbose output
        self.log = 'log/' + time.strftime("%Y-%m-%d") + '-fauna.log'
        self.issues = 'log/' + time.strftime("%Y-%m-%d") + '-fauna.issues'

        print("Run information can be found in " + self.log)
        print("Issues that arise can be found in "+ self.issues)

        # Deafault is most-used GISAID fasta headers, as described in nextstrain documentation
        self.fasta_headers = ['accession', 'strain', 'isolate_id', 'locus', 'passage', 'submitting_lab']
        # Define fields that will be used to construct unique indices in the fauna database
        self.index_fields = ['strain', 'date', 'gisaid_id', 'whatever']


    def read_fasta(self, infile):
        '''
        Take a fasta file and a list of information contained in its headers
        and build a dataset object from it.
        '''
        out = []
        with open(self.log, 'w') as log:
            t = time.strftime('%Y-%m-%d %H:%M:%S')
            log.write('['+t+']: Beginning to read ' + infile)

        # Read the fasta
        with open(infile, "rU") as f:

            for record in SeqIO.parse(f, "fasta"):
                data = {}
                head = record.id.split('|')
                for i in range(len(self.fasta_headers)):
                    data[self.fasta_headers[i]] = head[i]
                    data['sequence'] = str(record.seq)

        # Try/except clause goes here
                index = ''
                for ind in self.index_fields:
                    index += data[ind]
                out.append({index : data})
                # Format properly
        print(out)

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
        Make sure all new entries to the dataset
        '''
        match = True
        for key in data:
            if key not in self.dataset[0].keys():
                print('Error adding ' + key + 'to dataset, keys don\'t match.')
                match = False
        if match:
            self.dataset.append(data)

    def write(self, out_type, out_file):
        # TODO: lol, this didn't work, worth a shot
        if out_type == 'json':
            with open(out_file, 'w+') as f:
                json.dump(self.dataset, f)

    testout = args.outpath + 'output/test.json'
    D.write('json', testout, tabular=1)
