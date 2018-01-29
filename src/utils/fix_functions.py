import re

def strain_name(strain, original_name, logger):
    """ copied from "fix_name" fn in fauna """
    name = original_name.replace(' ', '').replace('\'', '').replace('(', '').replace(')', '').replace('H3N2', '').replace('Human', '').replace('human', '').replace('//', '/').replace('.', '').replace(',', '').replace('duck', '').replace('environment', '')
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
        else:
            print("Couldn't reformat this date: " + date + ", setting to None")
            date = None
    else:
        date = None
    if date is not original_date:
        logger.debug("Changed date from {} to {}".format(original_date, date))
    if date is None:
        logger.warn("Date for {} is None!".format(sample.parent.strain_id))
    return date
