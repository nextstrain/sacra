import csv
from misc import camelcase_to_snakecase

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


def parse_geo_synonyms(fname):
    '''
    open synonym to country dictionary (geo_synonyms.tsv)
    Location is to the level of country of administrative division when available
    '''
    reader = csv.DictReader(filter(lambda row: row[0]!='#', open(fname)), delimiter='\t') # list of dicts
    geo_synonyms = {"division": {}, "country": {}, "location": {}}
    for line in reader:
        geo_synonyms["location"][line['label'].decode('unicode-escape').lower()] = camelcase_to_snakecase(line['location'])
        geo_synonyms["division"][line['label'].decode('unicode-escape').lower()] = camelcase_to_snakecase(line['division'])
        geo_synonyms["country"][line['label'].decode('unicode-escape').lower()] = camelcase_to_snakecase(line['country'])
    return geo_synonyms
