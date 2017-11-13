import re

def fix_strain(docs, virus):
    fix_whole_name = define_strain_fixes(cfg.strain_fix_fname[virus])
    label_to_fix = define_location_fixes(cfg.label_fix_fname[virus])
    for doc in docs:
        # Fix this when switching docs to dict
        for key in doc:
            doc[key]['strain'] = fix_name(doc[key]['strain'], fix_whole_name, label_to_fix)[0]

def fix_name(name, fix_whole_name, label_to_fix):
    '''
    Fix strain names
    '''
    # replace all accents with ? mark
    original_name = name.encode('ascii', 'replace')
    # Replace whole strain names
    name = replace_strain_name(original_name, fix_whole_name)
    name = name.replace('H1N1', '').replace('H5N6', '').replace('H3N2', '').replace('Human', '')\
        .replace('human', '').replace('//', '/').replace('.', '').replace(',', '').replace('&', '').replace(' ', '')\
        .replace('\'', '').replace('>', '').replace('-like', '').replace('+', '')
    split_name = name.split('/')
    # check location labels in strain names for fixing
    for index, label in enumerate(split_name):
        if label.replace(' ', '').lower() in label_to_fix:
            split_name[index] = label_to_fix[label.replace(' ', '').lower()]
    name = '/'.join(split_name)
    name = flu_fix_patterns(name)

    # Strip leading zeroes, change all capitalization location field to title case
    split_name = name.split('/')
    if len(split_name) == 4:
        if split_name[1].isupper() or split_name[1].islower():
            split_name[1] = split_name[1].title()  # B/WAKAYAMA-C/2/2016 becomes B/Wakayama-C/2/2016
        split_name[2] = split_name[2].lstrip('0')  # A/Mali/013MOP/2015 becomes A/Mali/13MOP/2015
        split_name[3] = split_name[3].lstrip('0')  # A/Cologne/Germany/01/2009 becomes A/Cologne/Germany/1/2009
    result_name = '/'.join(split_name).strip()
    return result_name, original_name

def replace_strain_name(original_name, fixes={}):
    '''
    return the new strain name that will replace the original
    '''
    if original_name in fixes:
        return fixes[original_name]
    else:
        return original_name

def define_strain_fixes(fname):
    '''
    Open strain name fixing files and define corresponding dictionaries
    '''
    reader = csv.DictReader(filter(lambda row: row[0]!='#', open(fname)), delimiter='\t')
    fix_whole_name = {}
    for line in reader:
        fix_whole_name[line['label'].decode('unicode-escape')] = line['fix']
    return fix_whole_name

def define_location_fixes(fname):
    reader = csv.DictReader(filter(lambda row: row[0]!='#', open(fname)), delimiter='\t')
    label_to_fix = {}
    for line in reader:
        label_to_fix[line['label'].decode('unicode-escape').replace(' ', '').lower()] = line['fix']
    return label_to_fix

def flu_fix_patterns(name):
    # various name patterns that need to be fixed
    # capitalization of virus type
    if re.match(r'([a|b])([\w\s\-/]+)', name):  #b/sydney/508/2008    B/sydney/508/2008
        name = re.match(r'([a|b])([\w\s\-/]+)', name).group(1).upper() + re.match(r'([a|b])([\w\s\-/]+)', name).group(2)
    # remove inner parentheses and their contents
    if re.match(r'([^(]+)[^)]+\)(.+)', name):  # A/Egypt/51(S)/2006
        name = re.match(r'([^(]+)[^)]+\)(.+)', name).group(1) + re.match(r'([^(]+)[^)]+\)(.+)', name).group(2)
    # remove ending parentheses and their contents
    if re.match(r'([^(]+)[^)]+\)$', name):  # A/Eskisehir/359/2016 (109) -> A/Eskisehir/359/2016 ; A/South Australia/55/2014  IVR145  (14/232) -> A/South Australia/55/2014  IVR145
        name = re.match(r'([^(]+)[^)]+\)$', name).group(1)
    # Add year info to these Hongkong sequences
    if re.match(r'A/HongKong/H090-[0-9]{3}-V[0-9]$', name):  # A/HongKong/H090-750-V1 All confirmed from 2009
        name = name + "/2009"
    # Add year info to these Sendai sequences
    if re.match(r'A/Sendai/TU[0-9]{2}', name): # A/Sendai/TU08 All confirmed from 2010
        name = name + "/2010"
    # reformat names with clinical isolate in names, Philippines and Thailand
    if re.match(r'([A|B]/)clinicalisolate(SA[0-9]+)([^/]+)(/[0-9]{4})', name):  #B/clinicalisolateSA116Philippines/2002 -> B/Philippines/SA116/2002
        match = re.match(r'([A|B]/)clinicalisolate(SA[0-9]+)([^/]+)(/[0-9]{4})', name)
        name = match.group(1) + match.group(3) + "/" + match.group(2) + match.group(4)
    # reformat Ireland strain names
    if re.match(r'([1-2]+)IRL([0-9]+)$', name):  # 12IRL26168 -> A/Ireland/26168/2012  (All sequences with same pattern are H3N2)
        name = "A/Ireland/" + re.match(r'([1-2]+)IRL([0-9]+)$', name).group(2) + "/20" + re.match(r'([1-2]+)IRL([0-9]+)$', name).group(1)
    # Remove info B/Vic strain info from name
    if re.match(r'([\w\s\-/]+)(\(?)(B/Victoria/2/87|B/Victoria/2/1987)$', name):  # B/Finland/150/90 B/Victoria/2/1987 -> B/Finland/150/90
        name = re.match(r'([\w\s\-/]+)(\(?)(B/Victoria/2/87|B/Victoria/2/1987)$', name).group(1)
    # Separate location info from ID info in strain name
    if re.match(r'([A|B]/[^0-9/]+)([0-9]+[A-Za-z]*/[0-9/]*[0-9]{2,4})$', name):  #A/Iceland183/2009  A/Baylor4A/1983  A/Beijing262/41/1994
        name = re.match(r'([A|B]/[^0-9/]+)([0-9]+[A-Za-z]*/[0-9/]*[0-9]{2,4})$', name).group(1) + "/" + re.match(r'([A|B]/[^0-9/]+)([0-9]+[A-Za-z]*/[0-9/]*[0-9]{2,4})$', name).group(2)
    # Remove characters after year info, associated with passage info but can parse that from passage field later
    if re.match(r'([A|B]/[A-Za-z-]+/[A-Za-z0-9_-]+/[0-9]{4})(.)+$', name):  # B/California/12/2015BX59B A/Shanghai/11/1987/X99/highyieldingreassortant
        name = re.match(r'([A|B]/[A-Za-z-]+/[A-Za-z0-9_-]+/[0-9]{4})(.)+$', name).group(1)
    # Strip trailing slashes
    name = name.rstrip('/')  # A/NorthernTerritory/60/68//  A/Paris/455/2015/
    # Change two digit years to four digit years
    if re.match(r'([\w\s\-/]+)/([0-9][0-9])$', name):  #B/Florida/1/96 -> B/Florida/1/1996
        year = re.match(r'([\w\s\-/]+)/([0-9][0-9])$', name).group(2)
        if int(year) < 66:
            name = re.match(r'([\w\s\-/]+)/([0-9][0-9])$', name).group(1) + "/20" + year
        else:
            name = re.match(r'([\w\s\-/]+)/([0-9][0-9])$', name).group(1) + "/19" + year
    return name
