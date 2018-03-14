import re, sys
import csv
from misc import camelcase_to_snakecase, snakecase_to_camelcase
from file_readers import parse_geo_synonyms, make_dict_from_file

lookups = {
    "strain_name_to_strain_name": None,
    "strain_name_to_location": None,
    "strain_name_to_date": None,
    "country_to_region": None,
    "geo_synonyms": None
}

def attribution_id(obj, existing_id, logger):
    if hasattr(obj, "authors") and hasattr(obj, "attribution_date"):
        value = obj.authors + '|' + obj.attribution_date.split('-')[0]
    elif hasattr(obj, "authors"):
        value = obj.authors
    else:
        logger.warn("attribution_id set to None")
        value = None
    if existing_id and existing_id is not value:
        logger.warn("Attribution ID somehow provided and does not equal fixed ID ({} vs {})".format(existing_id, value))
    return value

def sample_name(obj, existing_name, logger):
    if existing_name:
        return existing_name
    obj.fix_single("collection_date")
    if obj.collection_date is None:
        return "unknown"
    return obj.collection_date


def strain_name(strain, original_name, logger):
    # the first time this function runs the database needs to be loaded into memory
    if lookups["strain_name_to_strain_name"] is None and sample.CONFIG["fix_lookups"]["strain_name_to_strain_name"] is not None:
        lookups["strain_name_to_strain_name"] = make_dict_from_file(sample.CONFIG["fix_lookups"]["strain_name_to_strain_name"])

    name = original_name

    if name in lookups["strain_name_to_strain_name"]:
        name = lookups["strain_name_to_strain_name"][name]

    name = (
        name.replace(' ', '').replace('\'', '').replace('(', '').replace(')', '').replace('//', '/').replace('.', '').replace(',', '')
            .replace('H3N2', '').replace('Human', '').replace('human', '').replace('duck', '').replace('environment', '')
        )
    try:
        name = 'V' + str(int(name))
    except:
        pass
    if name is not original_name:
        logger.debug("Changed strain name from {} to {}".format(original_name, name))
    return name

def collection_date(sample, original_date, logger):
    '''
    Format viruses date attribute: collection date in YYYY-MM-DD format, for example, 2016-02-28
    Input date could be YYYY_MM_DD, reformat to YYYY-MM-DD
    E.G. 2002_04_25 to 2002-04-25
    '''

    # the first time this function runs the database needs to be loaded into memory
    if lookups["strain_name_to_date"] is None and sample.CONFIG["fix_lookups"]["strain_name_to_date"] is not None:
        lookups["strain_name_to_date"] = make_dict_from_file(sample.CONFIG["fix_lookups"]["strain_name_to_date"])
    if lookups["strain_name_to_date"] is not None and sample.parent.strain_name in lookups["strain_name_to_date"]:
        date = lookups["strain_name_to_date"][sample.parent.strain_name]
    else:
        date = original_date

    if date is not None and date.strip() != '':
        date = re.sub(r'_', r'-', date)
        # ex. 2002-XX-XX or 2002-09-05
        if re.match(r'\d\d\d\d-(\d\d|XX)-(\d\d|XX)', date):
            pass
        # ex. 2002-2-4
        elif re.match(r'^\d\d\d\d-\d-\d$', date):
            date = re.sub(r'^(\d\d\d\d)-(\d)-(\d)$', r'\1-0\2-0\3', date)
        # ex. 2002-02-4
        elif re.match(r'^\d\d\d\d-\d\d-\d$', date):
            date = re.sub(r'^(\d\d\d\d)-(\d\d)-(\d)$', r'\1-\2-0\3', date)
        # ex. 2002-2-15
        elif re.match(r'^\d\d\d\d-\d-\d\d$', date):
            date = re.sub(r'^(\d\d\d\d)-(\d)-(\d\d)$', r'\1-0\2-\3', date)
        elif re.match(r'\d\d\d\d\s\(Month\sand\sday\sunknown\)', date):
            date = date[0:4] + "-XX-XX"
        # ex. 2009-06 (Day unknown)
        elif re.match(r'\d\d\d\d-\d\d\s\(Day\sunknown\)', date):
            date = date[0:7] + "-XX"
        elif re.match(r'\d\d\d\d-\d\d', date):
            date = date[0:7] + "-XX"
        elif re.match(r'\d\d\d\d', date):
            date = date[0:4] + "-XX-XX"
        # 15-Sep-2015
        elif re.match(r'^\d+-\w+-\d\d\d\d', date):
            groups = re.match(r'^(\d+)-(\w+)-(\d\d\d\d)', date).groups()
            month_str_to_num = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12", "january": "01", "february": "02", "march": "03", "april": "04", "june": "06", "july": "07", "august": "08", "sepember": "09", "october": "10", "november": "11", "december": "12"}
            day = groups[0]
            if len(day) == 1:
                day = '0' + day
            try:
                date = groups[2] + "-" + month_str_to_num[groups[1].lower()] + "-" + day
            except KeyError:
                date = groups[2] + "-XX-XX"
        else:
            logger.warn("Couldn't reformat this date: " + date + ", setting to None")
            date = None
    else:
        date = None
    if date is not original_date:
        logger.debug("Changed date from {} to {}".format(original_date, date))
    if date is None:
        logger.warn("Date for {} is None!".format(sample.parent.strain_id))
    return date

def country(sample, value, logger):
    return general_location_fix(sample, "country", value, logger)

def division(sample, value, logger):
    return general_location_fix(sample, "division", value, logger)

def location(sample, value, logger):
    return general_location_fix(sample, "location", value, logger)

def general_location_fix(sample, category, original_value, logger):
    """ takes a value, uses a lookup (via sample.CONFIG & using "category") and some regex rules to try and fix it.
    If the value is None, then we try to use sample.location to infer the correct value
    May use unicode strings
    """

    # the first time this function runs the databases needs to be loaded into memory
    if lookups["geo_synonyms"] is None and sample.CONFIG["fix_lookups"]["geo_synonyms"] is not None:
        lookups["geo_synonyms"] = parse_geo_synonyms(sample.CONFIG["fix_lookups"]["geo_synonyms"])
    if lookups["strain_name_to_location"] is not None and sample.parent.strain_id in lookups["strain_name_to_location"]:
        value = lookups["strain_name_to_location"][sample.parent.strain_id]

    value = original_value
    if value is None:
        # fallback to the "location" if it exists
        if category is not "location" and hasattr(sample, "location") and getattr(sample, "location") is not None:
            value = getattr(sample, "location")
        else:
            return None
    value = snakecase_to_camelcase(value)

    if lookups["geo_synonyms"] is not None:
        if category not in lookups["geo_synonyms"]:
            logger.warn("Cannot lookup {} in geo_synonyms!".format(category))
        else:
            try:
                value = lookups["geo_synonyms"][category][value]
            except KeyError:
                # 2. Lookup the first ".../XXX" (whole geo match)
                try:
                    label = re.match(r'^([^/]+)', value).group(1).lower()
                    value = lookups["geo_synonyms"][category][label]
                except (AttributeError, KeyError): # attribute error if the regex finds no groups. KeyError if it's not in the DB
                    # 3. check for partial geo match A/CHIBA-C/61/2014
                    try:
                        label = re.match(r'^([^\-^\/]+)', value).group(1).lower()
                        value = lookups["geo_synonyms"][category][label]
                    except (AttributeError, KeyError): # attribute error if the regex finds no groups. KeyError if it's not in the DB
                        # 4. check for partial geo match
                        try:
                            label = re.match(r'^([A-Z][a-z]+)[A-Z0-9]', value).group(1).lower()
                            value = lookups["geo_synonyms"][category][label]
                        except (AttributeError, KeyError): # attribute error if the regex finds no groups. KeyError if it's not in the DB
                            value = "_".join(value.split("_")).lower() # only run if the lookup fails
    else:
        value = "_".join(value.split("_")).lower() # only run if the lookup fails

    if value != original_value:
        logger.debug("Changed {} from {} to {}".format(category, original_value, value))

    return value;


def region(strain, original_region, logger):
    '''
    Label viruses with region based on country
    Due to the ordering in CONFIG, this runs _after_ country, division etc have been fixed
    '''

    if lookups["country_to_region"] is None and strain.CONFIG["fix_lookups"]["country_to_region"] is not None:
        lookups["country_to_region"] = make_dict_from_file(strain.CONFIG["fix_lookups"]["country_to_region"], "country", "region")

    if lookups["country_to_region"] is None:
        return original_region

    region = None

    if hasattr(strain, "country"):
        if strain.country in lookups["country_to_region"]:
            region = lookups["country_to_region"][strain.country]
        elif camelcase_to_snakecase(strain.country) in lookups["country_to_region"]:
            region = lookups["country_to_region"][camelcase_to_snakecase(strain.country)]
        else:
            logger.warn("Country -> Region mapping missing for {}".format(strain.country))

    if original_region and original_region != region:
        logger.warn("Region incompatability!?! Provided: {} Setting to: {}".format(original_region, region))
    return region
