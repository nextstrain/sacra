from __future__ import division, print_function
import sys, re
sys.path.append("")
from src.default_config import default_config, common_fasta_headers
from src.utils.file_readers import make_dict_from_file
import src.utils.fix_functions as fix_functions

### modification functions ###
name_fix_dict = make_dict_from_file("source-data/zika_strain_name_fix.tsv")
date_fix_dict = make_dict_from_file("source-data/zika_date_fix.tsv")


def fix_strain_name(obj, name, logger):
        original_name = name
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
        if name is not original_name:
            logger.debug("Changed strain name from {} to {}".format(original_name, name))
        return name

def make_config(args, logger):
    """ make the function - you can use the args to customise it. Try to minimise the customisation! """
## initialise with default config
    config = default_config
    config["pathogen"] = "zika"
    if args.overwrite_fasta_header:
        if args.overwrite_fasta_header == "alt1":
            # ['BCCDC75', 'MuVs/No_designation_vaccine_related/A', '2017-02-28', 'human', 'canada', 'british_columbia', 'A']
            config["fasta_headers"] = [
                "accession",
                'strain_name',
                'collection_date',
                'host',
                'country',
                'division',
                'muv_genotype'
            ]
        elif args.overwrite_fasta_header == "fauna":
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
        else:
            logger.critical("Unknown FASTA header format demanded: \"{}\"".format(args.overwrite_fasta_header)); sys.exit(2)
    else:
        config["fasta_headers"] = [
            'strain_name',
            'virus',
            'accession',
            'collection_date',
            'country',
            'division',
            'muv_genotype',
            'host',
            'authors',
            'publication_name',
            'journal',
            'attribution_url',
            'accession_url'
        ]
    config["fix_functions"]["strain_name"] = fix_strain_name
    config["fix_lookups"]["strain_name_to_location"] = "source-data/zika_location_fix.tsv"
    config["fix_lookups"]["strain_name_to_date"] = "source-data/zika_date_fix.tsv"
    return config
