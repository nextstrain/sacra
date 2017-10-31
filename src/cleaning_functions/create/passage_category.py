import re

def create_passage_category(doc, *args):
    '''
    Separate passage into general categories, update document with determined category or None
    Regex borrowed from McWhite et al. 2016
    '''
    if 'passage' in doc and doc['passage'] is not None:
        passage = doc['passage'].upper()
        passage_category = "undetermined"
        if re.search(r'AM[1-9]|E[1-9]|AMNIOTIC|EGG|EX|AM_[1-9]', passage):   # McWhite
            passage_category = "egg"
        elif re.search(r'AM-[1-9]|EMBRYO|E$', passage):
            passage_category = "egg"
        elif re.search(r'LUNG|P0|OR_|ORIGINAL|CLINICAL|DIRECT', passage):    # McWhite
            passage_category = "unpassaged"
        elif re.search(r'ORGINAL|ORIGNAL|CLINCAL|THROAT|PRIMARY|NASO|AUTOPSY|BRONCHIAL|INITIAL|NASAL|NOSE|ORIG|SWAB', passage):
            passage_category = "unpassaged"
        elif re.search(r'TMK|RMK|RHMK|RII|PMK|R[1-9]|RX', passage):    # McWhite
            passage_category = "cell"
        elif re.search(r'S[1-9]|SX|SIAT|MDCK|MCDK|C[1-9]|CX|M[1-9]|MX|X[1-9]|^X_$', passage):  # McWhite
            passage_category = "cell"
        elif re.search(r'C_[1-9]|C [1-9]|MD[1-9]|MK[1-9]|MEK[1-9]', passage):
            passage_category = "cell"
        elif re.search(r'[Cc][Ee][Ll][Ll]', passage):
            passage_category = "cell"
        elif re.search(r'^S[1-9]_$| ^SX_$|SIAT2_SIAT1|SIAT3_SIAT1', passage):    # McWhite
            passage_category = "cell"
        elif re.search(r'UNKNOWN|UNDEFINED|NOT SPECIFIED|DIFFERENT ISOLATION SOURCES', passage):
            pass
        doc['passage_category'] = passage_category
    # Remove this for all 'create' fxns
    # else:
    #     doc['passage_category'] = "undetermined"

    if 'passage' in doc:
        doc.pop('passage',None)
