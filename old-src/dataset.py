from __future__ import division, print_function
import logging
import json
import os, sys
from cluster import Cluster
logger = logging.getLogger(__name__)
from entrez import query_genbank
from utils.genbank_parsers import process_genbank_record
from utils.populate_lookups import populate_lookups

flatten = lambda l: [item for sublist in l for item in sublist]

class Dataset:

    # Initializer
    def __init__(self, CONFIG):
        self.CONFIG = CONFIG
        self.clusters = []
        self.genbank_data = {}
        populate_lookups(self.CONFIG)

    # File handling
    def read_to_clusters(self, f):
        logger.info("Initializing sacra parse of files ---")
        ftype = self.infer_ftype(f)
        if ftype == "accessions":
            accessions = self.get_accessions_from_file(f)
            self.download_entrez_data(accessions, make_clusters=True)
        elif ftype == "fasta":
            unmerged_clusters = self.read_fasta_to_clusters(f)
            self.merge_clusters_into_state(unmerged_clusters)
        elif ftype == "json":
            unmerged_clusters = self.read_json_to_clusters(f)
            self.merge_clusters_into_state(unmerged_clusters)
        else:
            logger.error("Unknown input filetype for {}. Fatal.".format(f))
            sys.exit(2)


    def read_fasta_to_clusters(self, infile):
        from Bio import SeqIO
        '''
        Take a fasta file and a list of information contained in its headers
        and build a dataset object from it.

        # TODO: This should return a docs structure
        # (list of docs dicts) instead of its current behavior
        '''
        logger.info('Reading in FASTA from %s.' % (infile))

        clusters = []
        # Read the fasta
        with open(infile, "rU") as f:

            for record in SeqIO.parse(f, "fasta"):
                data = {}
                head = record.description.split('|')
                for i in range(len(self.CONFIG["fasta_headers"])):
                    try:
                        data[self.CONFIG["fasta_headers"][i]] = head[i]
                        data['sequence'] = str(record.seq)
                    except KeyError:
                        logger.critical("Error parsing FASTA header. Header: {}. CONFIG specifies: {}".format(head, self.CONFIG["fasta_headers"])); sys.exit(2)
                if self.CONFIG["custom_fields"] != {}:
                    for field in self.CONFIG["custom_fields"].keys():
                        data[field] = self.CONFIG["custom_fields"][field]
                # logger.debug("Processing this header: {}".format(data))
                clus = Cluster(self.CONFIG, data)
                att = Cluster(self.CONFIG, data, cluster_type="attribution")
                # link the attribute id to each sequence in the cluster
                self.link_attribution_id(clus, att)

                if clus.is_valid(): clusters.append(clus)
                if att.is_valid():
                    clusters.append(att)
                else:
                    logger.warn("Invalid attribution cluster")
        return clusters

    def read_json_to_clusters(self, infile):
        from strain import Strain
        from sample import Sample
        from sequence import Sequence
        from attribution import Attribution

        strains = []
        samples = []
        sequences = []
        attributions = []
        # Read file
        with open(infile, 'r') as f:
            for key, value in json.load(f).iteritems():
                # Keys should be "strains, samples, sequences, attributions, and dbinfo"
                if key == "dbinfo":
                    pass
                elif key == "strains":
                    for d in value:
                        try:
                            strains.append(Strain(self.CONFIG, d))
                        except:
                            logger.critical("Error reading strain block:\n {}".format(d)); sys.exit(2)
                elif key == "samples":
                    for d in value:
                        try:
                            samples.append(Sample(self.CONFIG, d, None))
                        except:
                            logger.critical("Error reading sample block:\n {}".format(d)); sys.exit(2)
                elif key == "sequences":
                    for d in value:
                        try:
                            sequences.append(Sequence(self.CONFIG, d, None))
                        except:
                            logger.critical("Error reading strain block:\n {}".format(d)); sys.exit(2)
                elif key == "attributions":
                    for d in value:
                        try:
                            attributions.append(Attribution(self.CONFIG, d))
                        except:
                            logger.critical("Error reading attribution block:\n {}".format(d)); sys.exit(2)

            clusters = self.build_clusters_from_unlinked_units(strains, samples, sequences, attributions)

        return clusters

    def build_clusters_from_unlinked_units(self, strains, samples, sequences, attributions):

        clusters = []

        if strains is not None:
            strains = self.pop_duplicate_entries(strains, "strain_id")
            if samples is not None:
                samples = self.pop_duplicate_entries(samples, "sample_id")
                if sequences is not None:
                    sequences = self.pop_duplicate_entries(sequences, "sequence_id")
                else:
                    logger.error("Error in build_clusters_from_unlinked_units; no sequences objects found")
            else:
                logger.error("Error in build_clusters_from_unlinked_units; no samples objects found")
        else:
            logger.error("Error in build_clusters_from_unlinked_units; no strains objects found")
        if attributions is not None:
            attributions = self.pop_duplicate_entries(attributions, "attribution_id")
        else:
            logger.error("Error in build_clusters_from_unlinked_units; no attributions objects found")

        for strain in strains:
            clus = Cluster(self.CONFIG, None, cluster_type="unlinked")
            clus.strains.add(strain)
            for sample in samples:
                sample_strain_name = sample.sample_id.split('|')[0]
                if sample_strain_name == strain.strain_id:
                    clus.samples.add(sample)
                    sample.parent = strain
                    strain.children.append(sample)
                    for sequence in sequences:
                        sequence_sample_name = sequence.sequence_id.split('|')[1]
                        sequence_strain_name = sequence.sequence_id.split('|')[0]
                        if sequence_sample_name == sample.sample_id.split('|')[1] and sequence_strain_name == strain.strain_id:
                            clus.sequences.add(sequence)
                            sequence.parent = sample
                            sample.children.append(sequence)
                        else:
                            pass
                else:
                    pass
            clus.cluster_type = "genic"
            clusters.append(clus)

        for attribution in attributions:
            clus = Cluster(self.CONFIG, None, cluster_type="unlinked")
            clus.attributions = set([attribution])
            clus.cluster_type = "attribution"
            clusters.append(clus)

        return clusters


    def pop_duplicate_entries(self, items, attr):
        remove = []
        for i in range(len(items)):
            for j in range(i+1,len(items)):
                if getattr(items[i], attr) == getattr(items[j], attr):
                    logger.debug("Found duplicate entries for {}, removing extras.".format(items[j]))
                    remove.append(j)
        list(set(remove)).sort()
        remove = remove[::-1]
        for index in remove:
            items.pop(index)
        return items

    def parse_gb_file(self, gb):
        '''
        Parse genbank file
        :return: list of documents(dictionaries of attributes) to upload
        '''
        try:
            handle = open(gb, 'r')
        except IOError:
            raise Exception(gb, "not found")
        else:
            return self.parse_gb_entries(handle)

    def parse_gb_entries(self, handle):
        '''
        Go through genbank records to get relevant virus information
        '''
        from Bio import SeqIO
        from utils.genbank_parsers import convert_gb_date
        metadata = {}
        SeqIO_records = SeqIO.parse(handle, "genbank")
        for record in SeqIO_records:
            r = {}
            r['source'] = 'genbank'
            r['accession'] = re.match(r'^([^.]*)', record.id).group(0).upper()  # get everything before the '.'?
            r['sequence'] = str(record.seq).lower()
            # set up as none and overwrite
            r["title"] = None
            r['authors'] = None
            r["puburl"] = None
            r["journal"] = None
            print("Processing genbank file for " + r['accession'])
            # all the references (i.e. the papers / direct-submission notes)
            references = record.annotations["references"]

            if len(references):
                # is there a reference which is not a "Direct Submission"?
                titles = [reference.title for reference in references]
                try:
                    idx = [i for i, j in enumerate(titles) if j is not None and j != "Direct Submission"][0]
                except IndexError: # fall back to direct submission
                    idx = [i for i, j in enumerate(titles) if j is not None][0]
                reference = references[idx] # <class 'Bio.SeqFeature.Reference'>
                keys = reference.__dict__.keys()
                r['title'] = reference.title
                if "authors" in keys and reference.authors is not None:
                    first_author = re.match(r'^([^,]*)', reference.authors).group(0)
                    r['authors'] = first_author + " et al"
                if "journal" in keys and reference.journal is not None:
                    r['journal'] = reference.journal
                if "pubmed_id" in keys and reference.pubmed_id is not None:
                    r["puburl"] = "https://www.ncbi.nlm.nih.gov/pubmed/" + reference.pubmed_id
            else:
                print("Couldn't find the reference for " + s['accession'])

            # print(" *** Accession: {} title: {} authors: {} journal: {} paperURL: {}".format(s['accession'], s['title'], s['authors'], s['journal'], s['puburl']))

            s['url'] = "https://www.ncbi.nlm.nih.gov/nuccore/" + s['accession']
            #s['url'] = self.get_doi_url(url, s['title'], first_author)

            record_features = record.features
            for feat in record_features:
                if feat.type == 'source':
                    qualifiers = feat.qualifiers
                    if 'collection_date' in qualifiers:
                        r['collection_date'] = convert_gb_date(qualifiers['collection_date'][0])
                    if 'country' in qualifiers:
                        r['country'] = re.match(r'^([^:]*)', qualifiers['country'][0]).group(0)
                    if 'strain' in qualifiers:
                        r['strain'] = qualifiers['strain'][0]
                    elif 'isolate' in qualifiers:
                        r['strain'] = qualifiers['isolate'][0]
                    else:
                        print("Couldn't parse strain name for " + s['accession'])
            metadata[r['strain']] = r
        handle.close()
        print(str(len(metadata)) + " genbank entries parsed")
        return metadata

    def get_accessions_from_file(self, fname):
        accessions = []
        try:
            with open(fname, "r") as f:
                for line in f:
                    accessions.append(line.strip())
        except IOError:
            logger.error("File {} could not be read. Skipping.".format(fname))
        return accessions

    # Random utils
    def infer_ftype(self, fname):
        if fname.endswith(".fasta"):
            return "fasta"
        if fname.endswith(".txt"):
            return "accessions"
        elif (fname.endswith(".json")):
            return "json"

    def download_entrez_data(self, accessions, make_clusters = False):
        ## don't fetch data that's already fetched!
        new_accs = [x for x in accessions if x not in self.genbank_data.keys()]
        logger.info("Fetching {} additional genbank entries".format(len(new_accs)))
        if len(new_accs):
            new_data = query_genbank(new_accs)
            for k, v in new_data.iteritems():
                self.genbank_data[k] = v

        if make_clusters:
            data_dicts = [process_genbank_record(accession, record, self.CONFIG) for \
                accession, record in self.genbank_data.iteritems() if accession in accessions]
            unmerged_clusters = []
            for d in data_dicts:
                clus = Cluster(self.CONFIG, d)
                att = Cluster(self.CONFIG, d, cluster_type="attribution")
                # link the attribute id to each sequence in the cluster
                self.link_attribution_id(clus, att)
                if clus.is_valid(): unmerged_clusters.append(clus)
                if att.is_valid(): unmerged_clusters.append(att)
            self.merge_clusters_into_state(unmerged_clusters)


    def link_attribution_id(self, genomic_cluster, attribution_cluster):
        if attribution_cluster.is_valid() and genomic_cluster.is_valid():
            for s in genomic_cluster.sequences:
                logger.debug("Setting attribution id {} for sequence {}".format(attribution_cluster.get_all_units()[0].attribution_id, s))
                s.attribution_id = attribution_cluster.get_all_units()[0].attribution_id
        else:
            if not attribution_cluster.is_valid():
                logger.warn("Invalid cluster: {}".format(attribution_cluster))
            elif genomic_cluster.is_valid():
                logger.warn("Invalid cluster: {}".format(genomic_cluster))

    def get_all_accessions(self):
        '''
        Read through all clusters to generate accession list for
        batch submission to entrez
        '''
        flatten = lambda l: [item for sublist in l for item in sublist]
        accs = flatten([c.get_all_accessions() for c in self.clusters])
        if len(accs) > 10:
            logger.debug("These are the first 10 accessions: {}".format(accs[:10]))
        else:
            logger.debug("These are the accessions: {}".format(accs))
        return accs

    # Merging and cleaning
    def merge_clusters_into_state(self, clusters):
        logger.debug("simply setting state to clusters!")
        self.clusters.extend(clusters)

    def refine_clusters_in_state(self):
        '''
        Read all clusters and merge clusters whose contents contain matching IDs
        '''
        genic_clusters = []
        attribution_clusters = []

        # Make sure that clusters look okay
        # This should probably be included in a cluster validation class method
        for cluster in self.clusters:
            if cluster.cluster_type == "genic":
                if len(cluster.strains) != 1:
                    logger.error("Genic cluster has more than one strain, removing.")
                    self.clusters.remove(cluster)
                else:
                    genic_clusters.append(cluster)
            elif cluster.cluster_type == "attribution":
                attribution_clusters.append(cluster)
            elif cluster.cluster_type == "titer":
                pass
            else:
                logger.error("Unknown cluster type, removing.")

        merged_out = []
        for i in range(len(genic_clusters)-1):
            for j in range(i+1,len(genic_clusters)):
                if genic_clusters[i].strains[0].strain_id == genic_clusters[j].strains[0].strain_id:
                    logger.info("Merging clusters on strain index {}".format(genic_clusters[i].strains[0].strain_id))
                    self.merge_two_genic_clusters(cluster1=genic_clusters[i], cluster2=genic_clusters[j])
                    merged_out.append(j)

        for i in range(len(attribution_clusters)-1):
            for j in range(i+1,len(attribution_clusters)):
                if attribution_clusters[i].attributions[0].attribution_id == attribution_clusters[j].attributions[0].attribution_id:
                    logger.info("Merging clusters on attribution index {}".format(attribution_clusters[i].attributions[0].attribution_id))
                    self.merge_two_attribution_clusters(cluster1=attribution_clusters[i], cluster2=attribution_clusters[j])
                    merged_out.append(j)

        # Remove the merged clusters
        for out in merged_out:
            self.clusters[out] = 'none'
        self.clusters = [x for x in self.clusters if x != 'none']
	print(self.clusters)

    def merge_two_genic_clusters(self, cluster1, cluster2):
        '''
        This function could be split into 5 parts:
            1. Current function
            2. merge_two_strains
            3. merge_two_samples
            4. merge_two_sequences
            5. merge_metadata
        '''
        mergable_metadata_fields = { "strain" : [],
                                     "sample" : [],
                                     "sequence" : [] }
        samples1 = list(cluster1.samples[:-1])
        samples2 = list(cluster2.samples[1:])
        for i in range(len(samples1)):
            sample1 = samples1[i]
            for j in range(i+1,len(samples2)):
                sample2 = samples2[j]
                # Check for matching samples
                if sample1.sample_id == sample2.sample_id:
                    for sequence1 in sample1.children:
                        for sequence2 in sample2.children:
                            if sequence1.sequence_id == sequence2.sequence_id:
                                for field in mergable_metadata_fields["sequence"]:
                                    #TODO: This should be more robust for metadata merges
                                    try:
                                        if getattr(sequence1, field) != getattr(sequence2, field):
                                            logger.error("Unmatched metadata ({}) for matching sequence ID {}: {} and {}.".format(field, sequence1.sequence_id, getattr(sequence1, field), getattr(sequcne2, field)))
                                        else:
                                            logger.debug("Successful merge for sequence ID {} on field {}.".format(sequence1.sequnce_id, field))
                                    except:
                                        logger.critical("Couldn't find field {} in sequence ID {}".format(field, sequence1.sequence_id))
                                sample2.children.remove(sequence2)
                    strain2.children.remove(sample2)
        for sample in samples2:
            for sequence in sample.children:
                cluster1.sequences.add(sequence)
                sequence.parent = sample
            cluster1.samples.add(sample)
            sample.parent = cluster1.strains[0]

    def merge_two_attribution_clusters(self, cluster1, cluster2):
        for field in self.CONFIG["mapping"]["attribution"]:
            if hasattr(cluster2, field):
                if hasattr(cluster1, field) and getattr(cluster1, field) != getattr(cluster2, field):
                    logger.warn("Clusters with matching id:{} have mismatched field:{} {} and {}".format(cluster1.attribution_id, field, getattr(cluster1, field), getattr(cluster2, field)))
                else:
                    setattr(cluster1, field, getattr(cluster2, field))

    def clean_clusters(self):
        logger.info("Cleaning clusters (move / fix / create / drop)")
        [c.clean() for c in self.clusters]

    # Output
    def write_to_json(self, filename):
        logger.info("writing to JSON: {}".format(filename))
        data = {"strains": [], "samples": [], "sequences": [], "attributions": []}
        data["dbinfo"] = {"pathogen": self.CONFIG["pathogen"]}
        for c in self.clusters:
            for n in ["strains", "samples", "sequences", "attributions"]:
                if hasattr(c, n): # if, e.g., "sequences" (n) is in the cluster (c)
                    data[n].extend([x.get_data() for x in getattr(c, n) if x.is_valid()])
        # remove empty values
        for table in data:
            if table == "dbinfo": continue
            for block in data[table]:
                for key in block.keys():
                    if block[key] in [None, '', '?', 'unknown', "Unknown"]:
                        del block[key]
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, ensure_ascii=False)
