import re

def camelcase_to_snakecase(name):
    '''
    convert camelcase format to snakecase format
    :param name:
    :return:
    '''
    if name is not None:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(" ", "")

def snakecase_to_camelcase(name):
    if name is not None:
        split_name = name.split('_')
        split_name = [x.title() for x in split_name]
        return "".join(split_name)
