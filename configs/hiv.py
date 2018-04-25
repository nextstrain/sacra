from __future__ import division, print_function
import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.file_readers import make_dict_from_file
import src.utils.fix_functions as fix_functions

######## lassa.py, config for lassa builds and config tutorial ########
'''
This file establishes the config for running Sacra builds for lassa

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
def fix_strain_name(obj, name, logger):
    """Return the input strain name."""
    return name

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
    config["pathogen"] = "hiv"
    '''
    Options can be added based on arguments specified by src/run.py
    You can add new arguments to the run script, and build logic around
    them here. Below is an example for the --overwrite_fasta_header flag.

    NOTE: addition of command line arguments is not recommended, most changes
    should happen through direct modification of this function.
    '''
    # >A1.RW.2007.R880_MPL_C11.KP223844
    config["fasta_headers"] = [
        'subtype',
        'country',
        'collection_date',
        'strain_name',
        'accession'
    ]
    config["fasta_separator_character"] = "."
    config["fasta_header_swaps"] = {
        "C.MW.2007.702010141_CH141.w12.KC156212": "C.MW.2007.702010141_CH141_w12.KC156212",
        "CD.MW.2008.CH492.PL.031108.UT.2.KY112314": "CD.MW.2008.CH492_PL_031108_UT_2.KY112314",
        "C.MW.2008.CH492.PL.031108.UT.12.KY112312": "C.MW.2008.CH492_PL_031108_UT_12.KY112312",
        "C.ZA.2006.C.CAP45.w65.455dps.4_17_T14B.JX976730": "C.ZA.2006.C_CAP45_w65_455dps_4_17_T14B.JX976730"
    }
    '''
    Make sure to add the fix functions that were defined above to the new config,
    otherwise they will never be executed and sacra will default to incorrect fxns.

    Inside of the config dictionary, there are sub-dicts for fix lookups by dictionary
    and for fix functions that are either defined above, or in sacra/src/utils/fix_functions.py
    '''
    config['fix_functions']['strain_name'] = fix_strain_name
    config["fix_lookups"]["strain_name_to_location"] = "source-data/hiv_location_fix.tsv"
    config["fix_lookups"]["strain_name_to_date"] = "source-data/hiv_date_fix.tsv"
    return config
