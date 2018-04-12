from __future__ import division, print_function
import utils.genbank_parsers as gbp
from cluster import Cluster
import re

def try_to_add_attributions_via_genbank(dataset):
    attribution_units = []
    non_att_clusters = [c for c in dataset.clusters if c.cluster_type != "attribution"]
    for cluster in non_att_clusters:
        seq_obj = cluster.sequences[0] # assume only one
        accession = seq_obj.accession
        print("accession: {}".format(accession))
        if not accession in dataset.genbank_data:
            print("{} NOT FOUND IN GENBANK DATA".format(accession))
            continue
        data = dataset.genbank_data[accession]
        source = [x for x in data.features if x.type == "source"][0].qualifiers
        reference = gbp.choose_best_reference(data)
        try:
            author = re.match(r'^([^,]*)', reference.authors).group(0) + " et al"
        except:
            print("setting author failed")
            author = "Unknown"

        attribution_journal = reference.journal
        if reference.pubmed_id is None:
            attribution_url = ""
        else:
            attribution_url = "https://www.ncbi.nlm.nih.gov/pubmed/" + reference.pubmed_id
        title = reference.title

        attribution_id = author

        already_seen = False
        ## have we seen this before?????
        for clus in dataset.clusters:
            if clus.cluster_type == "attribution" and clus.attributions[0].attribution_id == attribution_id:
                already_seen = True
                print("ALready seen" + attribution_id)

        if not already_seen:
            data_dictionary = {
                'attribution_id': attribution_id,
                'attribution_title': title,
                'attribution_journal': attribution_journal,
                'attribution_url': attribution_url,
                'authors': author
            }
            dataset.clusters.append(
                Cluster(dataset.CONFIG, data_dictionary, cluster_type="attribution")
            )

        # link the attribution id in the sequence cluster
        seq_obj.attribution_id = attribution_id









        # import pdb; pdb.set_trace()
