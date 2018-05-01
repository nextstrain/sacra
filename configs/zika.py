from __future__ import division, print_function
import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.file_readers import make_dict_from_file
import src.utils.fix_functions as fix_functions

######## zika.py, config for zika builds and config tutorial ########
'''
This file establishes the config for running Sacra builds for zika

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
name_fix_dict = make_dict_from_file("source-data/zika_strain_name_fix.tsv")
def fix_strain_name(obj, name, logger):
    '''
    This function modifies a single zika strain name.

    THIS IS WHERE DOC TESTS SHOULD GO
    '''
    original_name = name
    try:
        if name in name_fix_dict:
            name = name_fix_dict[name]
        name = name.replace('Zika_virus', '').replace('Zikavirus', '').replace('Zika virus', '').replace('Zika', '').replace('ZIKV', '')
        name = name.replace('Human', '').replace('human', '').replace('H.sapiens_wt', '').replace('H.sapiens_tc', '').replace('Hsapiens_tc', '').replace('H.sapiens-tc', '').replace('Homo_sapiens', '').replace('Homo sapiens', '').replace('Hsapiens', '').replace('H.sapiens', '')
        name = name.replace('/Hu/', '')
        name = name.replace('_Asian', '').replace('_Asia', '').replace('_asian', '').replace('_asia', '')
        name = name.replace('_URI', '').replace('_SER', '').replace('_PLA', '').replace('_MOS', '').replace('_SAL', '')
        name = name.replace('Aaegypti_wt', 'Aedes_aegypti').replace('Aedessp', 'Aedes_sp')
        name = name.replace(' ', '').replace('\'', '').replace('(', '').replace(')', '').replace('//', '/').replace('__', '_').replace('.', '').replace(',', '')
        name = re.sub('^[\/\_\-]', '', name)
        try:
            name = 'V' + str(int(name))
        except:
            pass
    except:
        logger.error("Error modifying Zika strain: {}".format(original_name))
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
            year = obj.parent.parent.collection_date.split('-')[-1]
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
    config["pathogen"] = "zika"
    '''
    Options can be added based on arguments specified by src/run.py
    You can add new arguments to the run script, and build logic around
    them here. Below is an example for the --custom_fasta_header flag.

    NOTE: addition of command line arguments is not recommended, most changes
    should happen through direct modification of this function.
    '''
    if args.custom_fasta_header:
        if args.custom_fasta_header == "fauna":
            config["fasta_headers"] = [
                'strain_name',
                'virus',
                'accession',
                'collection_date',
                'unused', # region
                'country',
                'division',
                'location',
                'unused', # genbank field
                'unused', # genome
                'authors',
                'accession_url',
                'publication_name',
                'journal',
                'attribution_url'
            ]
        elif args.custom_fasta_header == "sacra_rebuild":
            config["fasta_headers"] = [
                'accession',
                'authors',
                'attribution_journal',
                'segment',
                'unused',
                'attribution_url',
                'attribution_source',
                'strain_name',
                'unused',
                'attribution_title',
                'sequence_url',
                'pathogen',
                'collection_date',
                'country',
                'division',
                'host_species',
                'number_sequences',
                'region']
        elif args.custom_fasta_header == 'usvi':
            #USVI/13/2016|VI13|2016-08-13|usvi|saint_thomas|saint_thomas|miseq
            config['fasta_headers'] = [
                'strain_name',
                'accession',
                'collection_date',
                'country',
                'division',
                'subdivision',
                'platform']
        else:
            logger.critical("Unknown FASTA header format demanded: \"{}\"".format(args.custom_fasta_header)); sys.exit(2)
    else:
        # VIPR format is default
        config["fasta_headers"] = [
            "accession",
            'strain_name',
            'segment',
            'collection_date',
            'host',
            'country',
            'subtype',
            'virus_type'
        ]
    '''
    Make sure to add the fix functions that were defined above to the new config,
    otherwise they will never be executed and sacra will default to incorrect fxns.

    Inside of the config dictionary, there are sub-dicts for fix lookups by dictionary
    and for fix functions that are either defined above, or in sacra/src/utils/fix_functions.py
    '''
    config['mapping']['metadata'] = config['mapping']['strain'] + config['mapping']['sample'] + config['mapping']['sequence'] + config['mapping']['attribution']
    config["fix_functions"]["strain_name"] = fix_strain_name
    config["pre_merge_fix_functions"]["attribution"]["attribution_id"] = pre_merge_fix_attribution_id
    config["fix_functions"]["segment"] = fix_segment
    config["fix_lookups"]["strain_name_to_location"] = "source-data/zika_location_fix.tsv"
    config["fix_lookups"]["strain_name_to_date"] = "source-data/zika_date_fix.tsv"
    return config
