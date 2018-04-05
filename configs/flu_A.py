from __future__ import division, print_function
import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.file_readers import make_dict_from_file
import src.utils.fix_functions as fix_functions

### modified functions ###
name_fix_dict = make_dict_from_file("source-data/flu_A_strain_name_fix.tsv")
date_fix_dict = make_dict_from_file("source-data/flu_A_date_fix.tsv")

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

def fix_strain_name(obj, name, logger):
    original_name = name
    if name in name_fix_dict:
        name = name_fix_dict[name]
    name.encode('ascii', 'replace')
    name = name.replace('MuV/', '').replace('MuVi/', '').replace('MuVs/','')
    name = re.sub(r'[_ ]?\[([A-Z])\]$', r'/\1', name)
    name = re.sub(r'\(([A-Z])\)$', r'/\1', name)
    name = re.sub(r'_([A-Z])_$', r'/\1', name)
    name = re.sub(r'[ ;]', r'_', name)
    name = re.sub(r'//', r'/', name)
    name = name.replace('H1N1', '').replace('H5N6', '').replace('H3N2', '').replace('Human', '')
    name.replace('human', '').replace('//', '/').replace('.', '').replace(',', '').replace('&', '')
    name.replace(' ', '')
    name.replace('\'', '').replace('>', '').replace('-like', '').replace('+', '').replace('(PuertoRico', 'PuertoRico')

    name = flu_fix_patterns(name)

    # Strip leading zeroes, change all capitalization location field to title case
    split_name = name.split('/')
    if len(split_name) == 4:
        if split_name[1].isupper() or split_name[1].islower():
            split_name[1] = split_name[1].title()  # B/WAKAYAMA-C/2/2016 becomes B/Wakayama-C/2/2016
        split_name[2] = split_name[2].lstrip('0')  # A/Mali/013MOP/2015 becomes A/Mali/13MOP/2015
        split_name[3] = split_name[3].lstrip('0')  # A/Cologne/Germany/01/2009 becomes A/Cologne/Germany/1/2009
    name = '/'.join(split_name).strip()

    if name in name_fix_dict:
        name = name_fix_dict[name]
    if name is not original_name:
        logger.debug("Changed strain name from {} to {}".format(original_name, name))

    if name[0] == '_':
        name = name[1:]
    if name[-1] == '_':
        name = name[:-1]
    return name

def fix_host_species(obj, value, logger):
    num_slashes = obj.strain_name.count('/')
    if num_slashes == 4:
        return 'human'
    if num_slashes != 3:
        # print("Can't process this name (not 3 or 4 slashes)", obj.strain_name)
        return "other"
    potential_host = obj.strain_name.split('/')[1].lower().replace('-', '')
    if potential_host in obj.CONFIG["lookups"]["host_synonyms"]:
        return obj.CONFIG["lookups"]["host_synonyms"][potential_host]
    print(potential_host)
    return "other"

def fix_segment(obj, value, logger):
    # import pdb; pdb.set_trace()
    print("VALUE", value)
    return value

def fix_type(obj, value, logger):
    return obj.type.upper().strip('A/')

def fix_ha_type(obj, value, logger):
    if re.match(r'H(\d+)N', obj.type):
        return re.match(r'H(\d+)N', obj.type).group(1)
    return ''

def fix_na_type(obj, value, logger):
    if re.match(r'.*N(\d+)', obj.type):
        return re.match(r'.*N(\d+)', obj.type).group(1)
    return ''

def fix_lineage(obj, value, logger):
    logger.debug("get segment for", obj, value)
    return obj.lineage;

def fix_country(obj, value, logger):
    strain_name = obj.strain_id # (e.g.) A/duck/Australia/341/1983
    if '/' in strain_name:
        name = strain_name.split('/')[1]
        country = fix_functions.general_location_fix(obj, "country", name, logger)
        if not country:
            try:
                name = strain_name.split('/')[2]
            except IndexError:
                return ''
            country = fix_functions.general_location_fix(obj, "country", name, logger)
        return country
    logger.warn("don't know how to process country for ", strain_name)
    return ''

def make_config(args, logger):
    """ make the function - you can use the args to customise it. Try to minimise the customisation! """
    ## initialise with default config
    config = default_config
    config["pathogen"] = "flu_A"
    ## example: >114954 |  A/mallard/Gurjev/244/1982 | PB2 | A / H14N0 |  | 1982 (Month and day unknown)

    ## example: 1196114 | A/Connecticut/12/2018 | EPI_ISL_302943 | NP | Original | Centers for Disease Control and Prevention
    config["fasta_headers"] = [
        'accession',
        'strain_name',
        'sample_name',
        'segment',
        'passage',
        'sequencing_lab'
    ]
    config["mapping"]["sample"].extend(["type", "ha_type", "na_type", "lineage"])
    config["mapping"]["sequence"].extend(["segment"])
    config["fix_functions"]["strain_name"] = fix_strain_name
    config["fix_functions"]["host_species"] = fix_host_species
    config["fix_functions"]["segment"] = fix_segment
    config["fix_functions"]["type"] = fix_type
    config["fix_functions"]["ha_type"] = fix_ha_type
    config["fix_functions"]["na_type"] = fix_na_type
    config["fix_functions"]["lineage"] = fix_lineage
    config["fix_functions"]["country"] = fix_country
    config["fix_lookups"]["strain_name_to_location"] = "source-data/mumps_location_fix.tsv"
    config["fix_lookups"]["strain_name_to_date"] = "source-data/mumps_date_fix.tsv"
    config["lookups"]["host_synonyms"] = "source-data/fluA_host_synonyms.tsv"
    return config
