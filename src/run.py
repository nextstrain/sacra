from dataset import Dataset
import cfg as cfg
import argparse
import os, sys, time
sys.path.append('')

def assert_valid_input(pathogen, datatype, path, outpath, infiles, source, subtype, **kwargs):
    '''
    Make sure that all the given arguments are valid.
    '''
    assert pathogen.lower() in cfg.pathogens, 'Unknown pathogen, currently supported pathogens are: %s' % (", ".join(cfg.pathogens))
    assert datatype.lower() in cfg.datatypes, 'Unknown datatype, currently supported datatypes are: %s' % (", ".join(cfg.datatypes))
    assert os.path.isdir(path), 'Invalid input path: %s' % (path)
    if not os.path.isdir(outpath):
        print "Writing %s" % (path)
        os.makedirs(outpath)
    for infile in infiles:
        assert os.path.isfile(path+infile), 'Invalid input file: %s' % (infile)
    assert source.lower() in cfg.sources[datatype], 'Invalid source for %s data %s' % (datatype, source)
    if subtype:
        assert subtype in cfg.subtypes[pathogen], 'Invalid subtype %s for pathogen %s' % (subtype, pathogen)
    assert cfg.required_fields[datatype].issubset(cfg.optional_fields[datatype]), 'Not all required_fields for %s are listed in optional_fields.' % (datatype)

def list_options(list_pathogens, list_datatypes):
    if list_pathogens and list_datatypes:
        print 'Valid pathogens: %s' % (", ".join(cfg.pathogens))
        print 'Valid datatypes: %s' % (", ".join(cfg.datatypes))
        sys.exit()
    elif list_pathogens:
        print 'Valid pathogens: %s' % (", ".join(cfg.pathogens))
        sys.exit()
    elif list_datatypes:
        print 'Valid datatypes: %s' % (", ".join(cfg.datatypes))
        sys.exit()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--pathogen', default='seasonal_flu', type=str, help='pathogen type to be processed; default is seasonal_flu')
    parser.add_argument('-d', '--datatype', default='sequence', type=str, help='type of data being input; default is \"sequence\", other options are \"pathogen\" or \"titer\"')
    parser.add_argument('-p', '--path', default='data/', type=str, help='path to input file(s), default is \"data/\"')
    parser.add_argument('-m', '--metafile', default=None, type=str, help='name of file containing pathogen metadata')
    parser.add_argument('-o', '--outpath', default='output/', type=str, help='path to write output files; default is \"output/\"')
    parser.add_argument('-i', '--infiles', default=None, nargs='+', help='filename(s) to be processed')
    parser.add_argument('--source', default=None, type=str, help='data source')
    parser.add_argument('--subtype', default=None, type=str, help='subtype of pathogen')
    parser.add_argument('--list_pathogens', default=False, action='store_true', help='list all supported pathogens and exit')
    parser.add_argument('--list_datatypes', default=False,  action='store_true', help='list all supported datatypes and exit')
    parser.add_argument('--permissions', default='public', help='permissions level for documents in JSON')
    parser.add_argument('--test', default=False, action='store_true', help='test run for debugging') # Remove this at some point.
    args = parser.parse_args()

    list_options(args.list_pathogens, args.list_datatypes)
    assert_valid_input(**args.__dict__)

    if args.test:
        D = Dataset(**args.__dict__)
        # TODO: Add abstraction layer to read_data_files()
        # for read_and_clean_file()
        D.read_metadata(**args.__dict__)
        D.read_data_files(**args.__dict__)
        t = time.time()
        for key in D.dataset.keys():
            D.clean(key, D.dataset[key])
        # D.remove_bad_docs()
        print '~~~~~ Cleaned %s documents in %s seconds ~~~~~' % (len(D.dataset), (time.time()-t))
        D.build_references_table()
        D.set_sequence_permissions(args.permissions)
        D.write('%s%s_%s.json' % (args.outpath, args.pathogen, args.datatype))
