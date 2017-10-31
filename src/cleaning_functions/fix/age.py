def fix_age(doc, *args):
    '''
    Combine gisaid age information into one age field
    '''
    if 'age' in doc.keys() and doc['age'] is not None:
        if doc['age'].endswith('y') or doc['age'].endswith('m') or doc['age'].endswith('d'):
            pass
        else:
            try:
                str(doc['age'])
            except:
                print "Could not parse %s as a host age." % doc['age']
                doc['age'] = None
            else:
                doc['age'] = doc['age'] + 'y'
    else:
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
