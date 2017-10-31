import re

def fix_submitting_lab(doc, key, remove, *args):
    if 'submitting_lab' in doc and doc['submitting_lab'] is not None:
        if doc['submitting_lab'] == 'CentersforDiseaseControlandPrevention':
            doc['submitting_lab'] = 'CentersForDiseaseControlAndPrevention'
        doc['submitting_lab'] = camelcase_to_snakecase(doc['submitting_lab'])
    else:
        remove.append(key)

def camelcase_to_snakecase(name):
        '''
        convert camelcase format to snakecase format
        :param name:
        :return:
        '''
        if name is not None:
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(" ", "")
