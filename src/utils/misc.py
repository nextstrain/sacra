import csv
import re

def make_dict_from_file(fname):
    '''
    Open strain name fixing files and define corresponding dictionaries
    '''
    reader = csv.DictReader(filter(lambda row: row[0]!='#', open(fname)), delimiter='\t')
    fix_whole_name = {}
    for line in reader:
        if not line["fix"]:
            x = re.split(" +", line["label"])
            line["label"] = x[0]
            line["fix"] = x[1]
        fix_whole_name[line['label'].decode('unicode-escape')] = line['fix']
    return fix_whole_name
