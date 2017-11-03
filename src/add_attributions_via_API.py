from __future__ import print_function
import os, csv, sys, json, re
import logging
from pdb import set_trace
import argparse
from Bio import Entrez
from Bio import SeqIO
from functools import partial

parser = argparse.ArgumentParser()
parser.add_argument('--infile', required=True, type=str, help='data source')
parser.add_argument("--debug", "-d", action="store_const", dest="loglevel", const=logging.DEBUG, help="Enable debugging logging")

def parse_sacra_json(filename):
    try:
        with open(filename, 'r') as f:
            dataset = json.load(f)
        # verify the contents are consistent?
    except IOError:
        print("File not found")
        sys.exit(2)
    return dataset

def get_accessions(data):
    return set([x["accession"] for x in data["sequences"]])

def extract_attributions(data, record, **kwargs):
    accession = re.match(r'^([^.]*)', record.id).group(0).upper()  # get everything before the '.'?
    if accession not in data:
        logger.warn("Error with accession {}".format(accession))
        return
    references = record.annotations["references"]
    if len(references):
        # is there a reference which is not a "Direct Submission"?
        data[accession] = {}
        titles = [reference.title for reference in references]
        try:
            idx = [i for i, j in enumerate(titles) if j is not None and j != "Direct Submission"][0]
        except IndexError: # fall back to direct submission
            idx = [i for i, j in enumerate(titles) if j is not None][0]
        reference = references[idx] # <class 'Bio.SeqFeature.Reference'>
        keys = reference.__dict__.keys()
        data[accession]['title'] = reference.title
        if "authors" in keys and reference.authors is not None:
            first_author = re.match(r'^([^,]*)', reference.authors).group(0)
            data[accession]['authors'] = first_author + " et al"
        if "journal" in keys and reference.journal is not None:
            data[accession]['journal'] = reference.journal
        if "pubmed_id" in keys and reference.pubmed_id is not None:
            data[accession]["puburl"] = "https://www.ncbi.nlm.nih.gov/pubmed/" + reference.pubmed_id
        logger.debug("{} -> {}".format(accession, data[accession]))

    else:
        logger.debug("{} had no references".format(accession))


def query_genbank(accessions, parser, email=None, retmax=10, n_entrez=10, gbdb="nuccore", **kwargs):
    # https://www.biostars.org/p/66921/
    logger = logging.getLogger(__name__)
    if not email:
        email = os.environ['NCBI_EMAIL']
    Entrez.email = email
    logger.debug("Genbank email: {}".format(email))

    # prepare queries for download in chunks no greater than n_entrez
    queries = []
    for i in sorted(xrange(0, len(accessions), n_entrez)):
        queries.append(set(accessions[i:i+n_entrez]))

    def esearch(accs):
        if len(accs) == 0:
            logger.debug("No accessions left to search")
            return
        logger.debug("esearch with {}".format(accs))
        list_accs = list(accs)
        res = Entrez.read(Entrez.esearch(db=gbdb, term=" ".join(list_accs), retmax=retmax))
        if "ErrorList" in res:
            not_found = res["ErrorList"]["PhraseNotFound"][0]
            logger.debug("esearch failed - accession {} doesn't exist. Retrying".format(not_found))
            accs.remove(not_found)
            esearch(accs)
        else: # success :)
            for i, x in enumerate(list_accs):
                acc_gi_map[x] = res["IdList"][i]

    # populate Accession -> GI number via entrez esearch
    acc_gi_map = {x:None for x in accs}
    for qq in queries:
        esearch(qq)
    gi_numbers = [x for x in acc_gi_map.values() if x != None]

    # get entrez data vie efetch
    logger.debug("Getting epost results for {}".format(gi_numbers))
    try:
        search_handle = Entrez.epost(db=gbdb, id=",".join(gi_numbers))
        search_results = Entrez.read(search_handle)
        webenv, query_key = search_results["WebEnv"], search_results["QueryKey"]
    except:
        logger.critical("ERROR: Couldn't connect with entrez, please run again")
        sys.exit(2)
    for start in range(0, len(gi_numbers), retmax):
        #fetch entries in batch
        try:
            handle = Entrez.efetch(db=gbdb, rettype="gb", retstart=start, retmax=retmax, webenv=webenv, query_key=query_key)
        except IOError:
            logger.critical("ERROR: Couldn't connect with entrez, please run again")
        else:
            SeqIO_records = SeqIO.parse(handle, "genbank")
            for record in SeqIO_records:
                parser(record, **kwargs)


if __name__=="__main__":

    args = parser.parse_args()
    if not args.loglevel: args.loglevel = logging.INFO
    logging.basicConfig(level=args.loglevel, format='%(asctime)-15s %(message)s')
    logger = logging.getLogger(__name__)

    data = parse_sacra_json(args.infile)
    accs = get_accessions(data)

    attributions = {x: None for x in accs}
    extract_attributions_bind = partial(extract_attributions, attributions)

    query_genbank(accessions=list(accs), parser=extract_attributions_bind, **vars(args))
    set_trace()
