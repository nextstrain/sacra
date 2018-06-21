from __future__ import division, print_function
import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.file_readers import make_dict_from_file
import src.utils.fix_functions as fix_functions

######## rabies.py, config for rabies builds and config tutorial ########
'''
This file establishes the config for running Sacra builds for rabies

This config will also serve as a mini "tutorial" on how to build a sacra config for
a specific pathogen.

Note that the file is just named for the pathogen of interest, this will be referenced
in the command line call to sacra/src/run.py by the --pathogen flag.
'''

######## User-defined cleaning functions ########
'''
This is where a user can define their own cleaning functions that will be used
to canonicalize pathogen metadata.

All cleaning functions must follow the same structure:

1. Be named fix_<field name>
    This field name must match the attribute name that is being modified. Supported
    field names are listed under sacra/spec_mapping.py, and any unlisted field must
    be added so that fields can be sorted to the correct table.

2. Take arguments (obj, <attribute_name>, logger)
    a. obj: a reference to the unit object (i.e. strain object, sequence object, etc.)
       that has the modified field in its state.

       This gives access to obj.parent and obj.children, in the case that those references
       need to be made. Also gives access to the hasattr, getattr, and setattr methods
       on that object.

    b. <attribute_name>: can be anything, but this is the field that is being modified,
       so an informative name can be helpful.

    c. logger: this is a reference to a logger that is defined in
       sacra/src/utils/colorLogging.py. Logger can be used within cleaning functions
       to print information to stdout by calling logger.<log_level>("message").
       Log levels by priority (low to high):
          debug - only prints if the --debug flag is called from command line
          info - prints during all runs
          warning - for cases that may cause downstream erros in some cases
          error - for cases that will likely cause downstream errors
          critical - fatal errors; automatically kills process


3. Return a modified <attribute_name>
    Modifications to the state of obj can be made, but they may result in downstream
    errors. Expected behavior is that only the field specified will be changed.
'''
name_fix_dict = make_dict_from_file("source-data/rabies_strain_name_fix.tsv")
def fix_strain_name(obj, name, logger):
    '''
    This function modifies a single rabies strain name.

    THIS IS WHERE DOC TESTS SHOULD GO
    '''
    original_name = name
    if not name:
        return
    try:
        if name in name_fix_dict:
            name = name_fix_dict[name]
        name = name.replace('rabies_virus', '').replace('rabiesvirus', '').replace('rabies virus', '').replace('rabies', '').replace('RABV', '')
        name = name.replace('Canis familiaris', 'Canis_familiaris')
        name = name.replace(' ', '').replace('\'', '').replace('(', '').replace(')', '').replace('//', '/').replace('__', '_').replace('.', '').replace(',', '')
        name = re.sub('^[\/\_\-]', '', name)
    except:
        logger.error("Error modifying rabies strain: {}".format(original_name))
    if name is not original_name:
        logger.debug("Changed strain name from {} to {}".format(original_name, name))
    return name

def fix_segment(obj, seg, logger):
    '''
    '''
    return 'wholeGenome'

def pre_merge_fix_attribution_id(obj, attr_id, logger):
    """Overwrite the default method to fix attribution ID for merges.

    Return a modified attribution ID.

    Function contains two parts:
    1. Specific fixes and their reasoning (commented)
    2. General programmatic fixes

    Only applies to Attribution units (ignores sequences with attribution_id field)
    """

    if hasattr(obj, 'attribution_id') and obj.attribution_id is not None:
        return attr_id

    # Specific fixes
    ## Fix multiple Direct Submissions by a single lab.
    if hasattr(obj, 'authors') and hasattr(obj, 'attribution_journal'):
        if obj.attribution_title == "Direct Submission":
            new_id = obj.authors.split(' ')[0] + obj.attribution_journal.split(' ')[1]
            return new_id

    # Programmatic fixes
    if obj.unit_type != 'attribution':
        return attr_id
    else:
        if hasattr(obj, 'authors') and obj.authors is not None:
            new_id = obj.authors.split(' ')[0]
        else:
            new_id = ''
        if hasattr(obj.parent.parent, 'collection_date'):
            year = obj.parent.parent.collection_date.split('-')[0]
            new_id = new_id + year

        if hasattr(obj, 'attribution_title'):
            split_title = obj.attribution_title.split(' ')
            if len(split_title) > 1:
                first_two_words = split_title[0] + split_title[1]
                new_id = new_id + first_two_words
            elif len(split_title) == 1:
                first_word = split_title[0]
                new_id = new_id + first_word
        logger.debug("Set {} as attribution_id".format(new_id))
    return new_id

######## Config construction ########
def make_config(args, logger):
    '''
    This function builds and returns the config dictionary
    that will be passed through sacra.
    '''
    # Initialise with default config
    config = default_config
    '''
    Set pathogen name.
    IMPORTANT: Sacra run will fail if this field is not set.
    '''
    config["pathogen"] = "rabies"
    '''
    Options can be added based on arguments specified by src/run.py
    You can add new arguments to the run script, and build logic around
    them here. Below is an example for the --custom_fasta_header flag.

    NOTE: addition of command line arguments is not recommended, most changes
    should happen through direct modification of this function.
    '''
    config["fasta_headers"] = [
        "accession",
        'strain_name',
        'none'
    ]
    '''
    Make sure to add the fix functions that were defined above to the new config,
    otherwise they will never be executed and sacra will default to incorrect fxns.

    Inside of the config dictionary, there are sub-dicts for fix lookups by dictionary
    and for fix functions that are either defined above, or in sacra/src/utils/fix_functions.py
    '''
    config['fasta_separator_character'] = '.'
    config['mapping']['metadata'] = config['mapping']['strain'] + config['mapping']['sample'] + config['mapping']['sequence'] + config['mapping']['attribution']
    config["fix_functions"]["strain_name"] = fix_strain_name
    config["pre_merge_fix_functions"]["attribution"]["attribution_id"] = pre_merge_fix_attribution_id
    config["fix_functions"]["segment"] = fix_segment
    config["fix_lookups"]["strain_name_to_location"] = "source-data/rabies_location_fix.tsv"
    config["fix_lookups"]["strain_name_to_date"] = "source-data/rabies_date_fix.tsv"
    return config
