import os, time, datetime, csv, sys, json
import argparse
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
    def __init__(self):
        # Wrappers for data
        self.metadata = []
        self.dataset = []

        # Log files to cut down on verbose output
        self.date = time.strftime("%Y-%m-%d")
        self.log = self.date + '-fauna.log'
        print("Run information can be found in " + self.log)
        self.issues = self.date + '-fauna.issues'
        print("Issues that arise can be found in "+ self.issues)

        # TODO: make this accurate to what our most common input looks like
        # TODO: ask trevor about this
        self.fasta_headers = ['strain', 'virus', 'gisaid_id', 'date', 'region', 'country', 'division', 'city', 'passage', 'whatever']
        self.index_fields = ['strain', 'date', 'gisaid_id', 'whatever']


    def read_fasta(self, infile, headers=['strain', 'accession', 'date', 'host', 'country', 'division']):
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

                return
        # Merge the formatted dictionaries to self.dataset()

    def read_xml(self):
        '''
        Read an xml file to a metadata dataset
        '''
        return

    def merge(self, data):
        return

    def write(self, format):
        return

if name=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--datatype', default='sequence', help='type of data being input; default is \"sequence\", other options are \"virus\" or \"titer\"')

    parser.add_argument('--path', default='data/', help='path to input file, default is \"data/\"')
    parser.add_argument('--outpath', default='output/', help='path to write output files; default is \"output/\"')
    parser.add_argument('-i', '--infile', default=None, help='filename for file to be processed')
