import logging
import re

def extract_attributions(data, record, **kwargs):
    logger = logging.getLogger(__name__)
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
