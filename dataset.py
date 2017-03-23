import os, time, datetime, csv, sys, json
import argparse
from Bio import SeqIO

parser = argparse.ArgumentParser()
parser.add_argument('--datatype', default='sequence', help='type of data being input; default is \"sequence\", other options are \"virus\" or \"titer\"')

parser.add_argument('--path', default='data/', help='path to input file, default is \"data/\"')
parser.add_argument('--outpath', default='output/', help='path to write output files; default is \"output/\"')
parser.add_argument('-i', '--infile', default=None, help='filename for file to be processed')

class Dataset:
    def __init__(self):
        # Wrappers for data
        self.metadata = []
        self.dataset = []

        # Log files to cut down on verbose output
        # TODO: eventually make this an argparse option
        self.date = time.strftime("%Y-%m-%d")
        print(self.date)
        self.log = self.date + '-fauna.log'
        print(self.log)
        self.issues = self.date + '-fauna.issues'

        # TODO: make this accurate to what our most common input looks like
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
