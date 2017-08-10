import os, time, datetime, csv, sys, json
import cfg
from Bio import SeqIO
sys.path.append('')

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
    def __init__(self, datatype, virus, outpath, **kwargs):
        # Wrappers for data, described in class description
        self.metadata = {'datatype': datatype, 'virus': virus}
        self.dataset = {}

        # Track which documents should be removed
        self.bad_docs = []

        self.read_files(datatype, **kwargs)
        self.remove_seed()
        t = time.time()
        for key in self.dataset.keys():
            self.clean(key, self.dataset[key])
        self.remove_bad_docs()
        print '~~~~~ Cleaned %s documents in %s seconds ~~~~~' % (len(self.dataset), (time.time()-t))
        self.write('%s%s_%s.json' % (outpath, virus, datatype))

    def read_files(self, datatype, infiles, ftype, **kwargs):
        '''
        Look at all infiles, and determine what file type they are. Based in that determination,
        import each file individually.
        '''
        t = time.time()
        if datatype == 'sequence':
            fasta_suffixes = ['fasta', 'fa', 'f']
            # Set fields that will be used to key into fauna table, these should be unique for every document
            self.index_fields = ['accession']
            if ftype.lower() in fasta_suffixes:
                for infile in infiles:
                    self.read_fasta(infile, datatype=datatype, **kwargs)
            else:
                pass
        print '~~~~~ Read %s files in %s seconds ~~~~~' % (len(infiles), (time.time()-t))

    def read_fasta(self, infile, source, path, datatype, **kwargs):
        '''
        Take a fasta file and a list of information contained in its headers
        and build a dataset object from it.
        '''
        import cleaning_functions as cf
        print 'Reading in %s FASTA from %s%s.' % (source,path,infile)
        self.fasta_headers = cfg.fasta_headers[source.lower()]
        self.seed(datatype)

        out = []

        # Read the fasta
        with open(path + infile, "rU") as f:

            for record in SeqIO.parse(f, "fasta"):
                data = {}
                head = record.description.replace(" ","").split('|')
                for i in range(len(self.fasta_headers)):
                    data[self.fasta_headers[i]] = head[i]
                    data['sequence'] = str(record.seq)

                index = []
                for ind in self.index_fields:
                    try:
                        index.append(data[ind])
                    except:
                        pass
                out.append({":".join(index): data})

        # Merge the formatted dictionaries to self.dataset()
        print 'Fixing names for new documents'
        t = time.time()
        cf.format_names(out, self.metadata['virus'])
        print '~~~~~ Fixed names in %s seconds ~~~~~' % (time.time()-t)

        print 'Merging input FASTA to %s documents.' % (len(out))
        for doc in out:
            try:
                assert isinstance(doc, dict)
            except:
                print 'WARNING: Cannot merge doc of type %s: %s' % (type(doc), (str(doc)[:75] + '..') if len(str(doc)) > 75 else str(doc))
                pass
            assert len(doc.keys()) == 1, 'More than 1 key in %s' % (doc)
            self.merge(doc.keys()[0], doc[doc.keys()[0]])
        print 'Successfully merged %s documents. Done reading %s.' % (len(self.dataset)-1, infile)


    def read_xml(self):
        '''
        Read an xml file to a metadata dataset
        '''
        return

    def merge(self, key, data):
        '''
        Make sure all new entries to the dataset have formatted names
        '''
        self.dataset[key] = data

    def clean(self, key, doc):
        '''
        Take a document and return a canonicalized version of that document
        # TODO: Incorporate all the necessary cleaning functions
        '''
        # Remove docs with bad keys or that are not of type dict
        try:
            assert isinstance(doc, dict)
        except:
            print 'Documents must be of type dict, this one is of type %s:\n%s' % (type(doc), doc)
            return

        k = doc.keys()[0]

        # Use functions specified by cfg.py. Fxn defs in cleaning_functions.py
        if self.metadata['datatype'] == 'sequence':
            fxns = cfg.sequence_clean
        elif self.metadata['datatype'] == 'titer':
            fxns = cfg.titer_clean

        for fxn in fxns:
            fxn(doc, key, self.bad_docs, self.metadata['virus'])

    def remove_bad_docs(self):

        # Not working because of key errors, they should be ints
        if self.bad_docs != []:
            print 'Documents that need to be removed : %s ' % (self.bad_docs)
            self.bad_docs = self.bad_docs.sort().reverse()
            for key in self.bad_docs:
                t = self.dataset[key]
                self.dataset[key] = self.dataset[-1]
                self.dataset[-1] = t
                self.dataset.pop()

    def write(self, out_file):
        '''
        Write self.dataset to an output file, default type is json
        '''
        print 'Writing dataset to %s' % (out_file)
        t = time.time()
        out = {}
        for key in self.metadata.keys():
            out[key] = self.metadata[key]
        out['data'] = self.dataset

        with open(out_file, 'w+') as f:
            json.dump(out, f, indent=1)
	    print '~~~~~ Wrote output in %s seconds ~~~~~' % (time.time()-t)

    def seed(self, datatype):
        '''
        Make an empty entry in dataset that has all the necessary keys, acts as a merge filter
        '''
        seed = { field : None for field in cfg.optional_fields[datatype] }
        seed['sequence'] = None
        print 'Seeding with:'
        print seed
        self.dataset['seed'] = seed

    def remove_seed(self):
        # More efficient on large datasets than self.dataset = self.dataset[1:]
        self.dataset.pop('seed',None)
        # self.dataset[0] = self.dataset[-1]
        # self.dataset[-1] = t
        # self.dataset = self.dataset[:-1]
