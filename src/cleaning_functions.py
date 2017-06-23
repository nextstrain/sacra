import re
# Cleaning functions that will clean the data in a dataset object.
# These are kept separate from class functions to make it easier for the user to
# add their own functions specific to their own data.

# Currently all cleaning functions are from fauna1.0
# in the process of updating, will remove TODO flag from completed functions

def name_fix(doc):
    if 'strain' in doc:
        doc['strain'], doc['gisaid_strain'] = fix_name(doc['strain'])
    else:
        print("Missing strain name!")

def fix_casing(doc):
    '''
    fix gisaid specific fields casing
    '''
    for field in ['originating_lab', 'submitting_lab']:
        if field in doc and doc[field] is not None:
            doc[field] = doc[field].replace(' ', '_').replace('-', '_').lower()
    for field in ['gender', 'host', 'locus']:
        if field in doc and doc[field] is not None:
            doc[field] = self.camelcase_to_snakecase(doc[field])
    if 'accession' in doc and doc['accession'] is not None:
        doc['accession'] = 'EPI' + doc['accession']










####################################################
def fix_age(self, doc):
    # TODO
    '''
    Combine gisaid age information into one age field
    '''
    temp_age, temp_age_unit = None, None
    doc['age'] = None
    if 'Host_Age' in doc:
        try:
            temp_age = str(int(float(doc['Host_Age'])))
        except:
            pass
        del doc['Host_Age']
    if 'Host_Age_Unit' in doc:
        if isinstance(doc['Host_Age_Unit'], basestring):
            temp_age_unit = doc['Host_Age_Unit'].lower()
        else:
            temp_age_unit = 'y'
        del doc['Host_Age_Unit']
    if isinstance(temp_age, basestring) and isinstance(temp_age_unit, basestring):
        doc['age'] = temp_age + temp_age_unit
    return doc

def define_location_fixes(self, fname):
    # TODO
    reader = csv.DictReader(filter(lambda row: row[0]!='#', open(fname)), delimiter='\t')
    self.label_to_fix = {}
    for line in reader:
        self.label_to_fix[line['label'].decode('unicode-escape').replace(' ', '').lower()] = line['fix']

def fix_name(self, name):
    # TODO
    '''
    Fix strain names
    '''
    # replace all accents with ? mark
    original_name = name.encode('ascii', 'replace')
    # Replace whole strain names
    name = self.replace_strain_name(original_name, self.fix_whole_name)
    name = name.replace('H1N1', '').replace('H5N6', '').replace('H3N2', '').replace('Human', '')\
        .replace('human', '').replace('//', '/').replace('.', '').replace(',', '').replace('&', '').replace(' ', '')\
        .replace('\'', '').replace('>', '').replace('-like', '').replace('+', '')
    split_name = name.split('/')
    # check location labels in strain names for fixing
    for index, label in enumerate(split_name):
        if label.replace(' ', '').lower() in self.label_to_fix:
            split_name[index] = self.label_to_fix[label.replace(' ', '').lower()]
    name = '/'.join(split_name)
    name = self.flu_fix_patterns(name)

    # Strip leading zeroes, change all capitalization location field to title case
    split_name = name.split('/')
    if len(split_name) == 4:
        if split_name[1].isupper() or split_name[1].islower():
            split_name[1] = split_name[1].title()  # B/WAKAYAMA-C/2/2016 becomes B/Wakayama-C/2/2016
        split_name[2] = split_name[2].lstrip('0')  # A/Mali/013MOP/2015 becomes A/Mali/13MOP/2015
        split_name[3] = split_name[3].lstrip('0')  # A/Cologne/Germany/01/2009 becomes A/Cologne/Germany/1/2009
    result_name = '/'.join(split_name).strip()
    return result_name, original_name

def flu_fix_patterns(self, name):
    # TODO
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

def format_country(self, v):
    # TODO
    '''
    Label viruses with country based on strain name
    '''
    strain_name = v['strain']
    original_name = v['gisaid_strain']
    if 'gisaid_location' not in v or v['gisaid_location'] is None:
        v['gisaid_location'] = ''
    if '/' in strain_name:
        name = strain_name.split('/')[1]
        if any(place.lower() == name.lower() for place in ['SaoPaulo', 'SantaCatarina', 'Calarasi', 'England', 'Sc']):
            name = v['gisaid_location'].split('/')[len(v['gisaid_location'].split('/'))-1].strip()
            result = self.determine_location(name)
            if result is None:
                result = self.determine_location(strain_name.split('/')[1])
        else:
            result = self.determine_location(name)
    else:
        result = None
    if result is not None:
        v['location'], v['division'], v['country'] = result
    else:
        v['location'], v['division'], v['country'] = None, None, None
        print("couldn't parse country for ", strain_name, "gisaid location", v['gisaid_location'], original_name)

    # Repeat location name, Use gisaid Location to assign name
    repeat_location = {'BuenosAires': ('BuenosAires', 'Pernambuco', 'Brazil'), 'SantaCruz': ('SantaCruz', 'SantaCruz', 'Bolivia'),
                       'ChristChurch': ('ChristChurch', 'ChristChurch', 'Barbados'), 'SaintPetersburg': ('SaintPetersburg', 'Florida', 'USA'),
                        'GeorgiaCountry': ('GeorgiaCountry', 'GeorgiaCountry', 'GeorgiaCountry')}
    for repeat, assignment in repeat_location.items():
        if repeat in v['strain']:
            if 'gisaid_location' in v and assignment[0] in v['gisaid_location']:
                v['location'] = assignment[0]
                v['division'] = assignment[1]
                v['country'] = assignment[2]

def format_passage(self, doc, initial_field, new_field, **kwargs):
    # TODO
    '''
    Separate passage into general categories
    Regex borrowed from McWhite et al. 2016
    '''
    if initial_field in doc and doc[initial_field] is not None:
        passage = doc[initial_field].upper()
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
        doc[new_field] = passage_category
    else:
        doc[initial_field] = None
        doc[new_field] = None
