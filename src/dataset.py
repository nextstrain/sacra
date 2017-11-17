import os, time, datetime, csv, sys, json
import cfg
from Bio import SeqIO
from pdb import set_trace
sys.path.append('')
# sys.path.append('src/')
# import cleaning_functions as c

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
    def __init__(self, datatype, pathogen, outpath, **kwargs):
        # Wrappers for data, described in class description
        self.metadata = {'datatype': datatype, 'pathogen': pathogen}
        self.dataset = {}

        # New schema TODO: make dump use these fields
        self.dbinfo = {'pathogen' : pathogen}
        self.strains = {}
        self.samples = {}
        self.sequences = {}
        # Track which documents should be removed
        self.bad_docs = []

    def read_data_files(self, infiles, **kwargs):
        '''
        Look at all infiles, and determine what file type they are. Based in that determination, import each file individually.
        Files should be specified in the format:
          filename[:<filetype>[:<source>]]
        '''
        t = time.time()
        for infile in infiles:
            filetype = self.determine_filetype(infile)
            if filetype in ['fasta', 'delimited', 'excel', 'json']:
                self.read_clean_reshape(infile,filetype, **kwargs)
            else:
                print "Could not read %s, unknown filetype"

        print '~~~~~ Read %s file(s) in %s seconds ~~~~~' % (len(infiles), (time.time()-t))

    def determine_filetype(self, infile):
        '''
        Look at a file and determine what type of file it is.
        '''
        infile = infile.lower()
        # Parse if infile format is specified by user
        if len(infile.split(':')) > 1:
            return infile.split(':')[1]

        fasta_suffixes = ['fasta', 'fa', 'f']
        csv_tsv_suffixes = ['csv', 'tsv', 'txt']
        excel_suffixes = ['xls', 'xlsx']
        json_suffixes = ['json']

        if (True in [ infile.endswith(s) for s in fasta_suffixes ]):
            return 'fasta'
        elif (True in [ infile.endswith(s) for s in csv_tsv_suffixes ]):
            return 'delimited'
        elif (True in [ infile.endswith(s) for s in excel_suffixes ]):
            return 'excel'
        elif (True in [ infile.endswith(s) for s in json_suffixes ]):
            return 'json'
        else:
            return 'unknown'

###################################################
####### Read, clean, reshape, and merge functions #
###################################################

##### Control
    def read_clean_reshape(self, infile, ftype, **kwargs):
        '''
        infile:file -> docs:list(dict) -> reshaped_docs:set(dict)
        This function performs 4 primary functions:
          1. read in a file of a known type into a list of dictionaries called docs
          2. clean each doc in docs according to all functions in cleaning_functions
          3. reshape docs into a set of dicts and merge the dicts into self
        '''
        # Read in a file of a known type into a list of dictionaries
        if ftype == 'fasta':
            docs = self.read_fasta(infile, **kwargs)
        elif ftype != 'fasta':
            # TODO: other file types
            return

        # Clean each doc in docs according to all functions in cleaning_functions
        docs = [ self.clean(doc) for doc in docs ]

        # Reshape docs into a set of dicts
        # TODO: write self.reshape()
        reshaped_docs = self.reshape(docs)
        #
        # # merge the dicts into self
        # # TODO: write self.merge_reshaped_docs()
        # self.merge_reshaped_docs(reshaped_docs)

##### Read
    def read_fasta(self, infile, source, path, datatype, **kwargs):
        '''
        Take a fasta file and a list of information contained in its headers
        and build a dataset object from it.

        # TODO: This should return a docs structure
        # (list of docs dicts) instead of its current behavior
        '''
        import cleaning_functions as cf
        print 'Reading in %s FASTA from %s%s.' % (source,path,infile)
        self.fasta_headers = cfg.fasta_headers[source.lower()]

        docs = []

        # Read the fasta
        with open(path + infile, "rU") as f:

            for record in SeqIO.parse(f, "fasta"):
                data = {}
                head = record.description.replace(" ","").split('|')
                for i in range(len(self.fasta_headers)):
                    data[self.fasta_headers[i]] = head[i]
                    data['sequence'] = str(record.seq)
                docs.append(data)

        return docs

        # # Merge the formatted dictionaries to self.dataset()
        # print 'Fixing names for new documents'
        # t = time.time()
        # cf.format_names(out, self.metadata['pathogen'])
        # print '~~~~~ Fixed names in %s seconds ~~~~~' % (time.time()-t)
        #
        # print 'Merging input FASTA to %s documents.' % (len(out))
        # for doc in out:
        #     try:
        #         assert isinstance(doc, dict)
        #     except:
        #         print 'WARNING: Cannot merge doc of type %s: %s' % (type(doc), (str(doc)[:75] + '..') if len(str(doc)) > 75 else str(doc))
        #         pass
        #     assert len(doc.keys()) == 1, 'More than 1 key in %s' % (doc)
        #     self.merge(doc.keys()[0], doc[doc.keys()[0]])
        # print 'Successfully merged %s documents. Done reading %s.' % (len(self.dataset)-1, infile)

##### Clean
    def clean(self, doc):
        '''
        Take a document dictionary and return a canonicalized version of that document dictionary
        # TODO: Incorporate all the necessary cleaning functions
        '''
        # Remove docs with bad keys or that are not of type dict
        try:
            assert isinstance(doc, dict)
        except:
            print 'Documents must be of type dict, this one is of type %s:\n%s' % (type(doc), doc)
            return

        # Use functions specified by cfg.py. Fxn defs in cleaning_functions.py
        fxns = cfg.sequence_clean
        for fxn in fxns:
            fxn(doc, None, self.bad_docs, self.metadata['pathogen'])

        return doc

##### Reshape
    def reshape(self,docs):
        import spec_mapping as m
        for doc in docs:
            # Make new entries for strains, samples, and sequences
            # Walk downward through hierarchy
            # TODO: Think about what to do if only "sequence_name" is available for some reason

            if 'strain_name' in doc.keys():
                strain_id = doc['strain_name']
                if strain_id not in self.strains.keys():
                    self.strains[strain_id] = {}
                for field in doc.keys():
                    if field in m.mapping["strains"]:
                        self.strains[strain_id][field] = doc[field]
                doc['sample_strain_name'] = doc['strain_name']
                if 'sample_name' in doc.keys():
                    sample_id = strain_id + '|' + doc['sample_name']
                    if sample_id not in self.samples.keys():
                        self.samples[sample_id] = {}
                    for field in doc.keys():
                        if field in m.mapping["samples"]:
                            self.samples[sample_id][field] = doc[field]
                    doc['sequence_sample_name'] = doc['sample_name']
                    if 'sequence_name' in doc.keys():
                        sequence_id = sample_id + '|' + doc['sequence_name']
                        if sequence_id not in self.sequences.keys():
                            self.sequences[sequence_id] = {}
                        for field in doc.keys():
                            if field in m.mapping["sequences"]:
                                self.sequences[sequence_id][field] = doc[field]

##################################################
####### End of RCR functions #####################
##################################################


# Everything south of here should be considered depracated until
# it has been looked over and updated relative to the new JSON spec.


    def read_metadata(self, path, metafile, **kwargs):
        '''
        Read an xml file to a metadata dataset
        '''
        if metafile is not None:
            import pandas as pd
            xl = pd.ExcelFile(path + metafile)
            meta = xl.parse("Tabelle1")
            print meta.columns
            meta.columns = [x.lower() for x in meta.columns]
            print meta.columns
            for index, row in meta.iterrows():
                # TODO: this
                pass

    # def remove_bad_docs(self):
    #
    #     # Not working because of key errors, they should be ints
    #     if self.bad_docs != []:
    #         print 'Documents that need to be removed : %s ' % (self.bad_docs)
    #         self.bad_docs = self.bad_docs.sort().reverse()
    #         for key in self.bad_docs:
    #             t = self.dataset[key]
    #             self.dataset[key] = self.dataset[-1]
    #             self.dataset[-1] = t
    #             self.dataset.pop()

    def write(self, out_file):
        '''
        Write self.dataset to an output file, default type is json
        '''
        print 'Writing dataset to %s' % (out_file)
        t = time.time()
        out = {'dbinfo': [ {key: value} for key,value in self.dbinfo.iteritems() ],
               'strains': [],
               'samples': [],
               'sequences': []}
        for key, value in self.strains.iteritems():
            strain_id = {'strain_id': key}
            strain_data = value
            out['strains'].append(merge_two_dicts(strain_id,strain_data))
        for key, value in self.samples.iteritems():
            sample_id = {'sample_id': key}
            sample_data = value
            out['samples'].append(merge_two_dicts(sample_id,sample_data))
        for key, value in self.sequences.iteritems():
            sequence_id = {'sequence_id': key}
            sequence_data = value
            out['sequences'].append(merge_two_dicts(sequence_id,sequence_data))

        with open(out_file, 'w+') as f:
            json.dump(out, f, indent=1)
	    print '~~~~~ Wrote output in %s seconds ~~~~~' % (time.time()-t)

    def set_sequence_permissions(self, permissions, **kwargs):
        for a in self.dataset:
            self.dataset[a]['permissions'] = permissions

    def build_references_table(self):
        '''
        This is a placeholder function right now, it will build a reference
        table for each upload according to the spec:
        {
        "pubmed_id" : {
          "authors" : [
            "author1",
            "author2",
            "author3"
          ],
          "journal" : "journal name",
          "date" : "publication date",
          "sequence_names" : [
            "sequence_name1",
            "sequence_name2",
            "sequence_name3"
          ],
          "publication_name" : "name"
        }
        '''
        refs = {
        "pubmed_id" : {
          "authors" : [
            "author1",
            "author2",
            "author3"
          ],
          "journal" : "journal name",
          "date" : "publication date",
          "sequence_names" : [
            "sequence_name1",
            "sequence_name2",
            "sequence_name3"
          ],
          "publication_name" : "name"
        } }

        self.references = refs

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
