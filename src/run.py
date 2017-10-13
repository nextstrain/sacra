from dataset import Dataset
import cfg as cfg
import argparse
import os, sys
sys.path.append('')

def assert_valid_input(virus, datatype, path, outpath, infiles, source, subtype, ftype, **kwargs):
    '''
    Make sure that all the given arguments are valid.
    '''
    assert virus.lower() in cfg.viruses, 'Unknown virus, currently supported viruses are: %s' % (", ".join(cfg.viruses))
    assert datatype.lower() in cfg.datatypes, 'Unknown datatype, currently supported datatypes are: %s' % (", ".join(cfg.datatypes))
    assert ftype.lower() in cfg.filetypes, 'Unknown filetype, currently supported filetypes are: %s' % (", ".join(cfg.filetypes))
    assert os.path.isdir(path), 'Invalid input path: %s' % (path)
    if not os.path.isdir(outpath):
        print "Writing %s" % (path)
        os.makedirs(outpath)
    for infile in infiles:
        assert os.path.isfile(path+infile), 'Invalid input file: %s' % (infile)
    assert source.lower() in cfg.sources[datatype], 'Invalid source for %s data %s' % (datatype, source)
    if subtype:
        assert subtype in cfg.subtypes[virus], 'Invalid subtype %s for virus %s' % (subtype, virus)
    assert cfg.required_fields[datatype].issubset(cfg.optional_fields[datatype]), 'Not all required_fields for %s are listed in optional_fields.' % (datatype)

def list_options(list_viruses, list_datatypes):
    if list_viruses and list_datatypes:
        print 'Valid viruses: %s' % (", ".join(cfg.viruses))
        print 'Valid datatypes: %s' % (", ".join(cfg.datatypes))
        sys.exit()
    elif list_viruses:
        print 'Valid viruses: %s' % (", ".join(cfg.viruses))
        sys.exit()
    elif list_datatypes:
        print 'Valid datatypes: %s' % (", ".join(cfg.datatypes))
        sys.exit()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--virus', default='seasonal_flu', type=str, help='virus type to be processed; default is seasonal_flu')
    parser.add_argument('-d', '--datatype', default='sequence', type=str, help='type of data being input; default is \"sequence\", other options are \"virus\" or \"titer\"')
    parser.add_argument('-p', '--path', default='data/', type=str, help='path to input file(s), default is \"data/\"')
    parser.add_argument('-m', '--metafile', default=None, type=str, help='name of file containing virus metadata')
    parser.add_argument('-o', '--outpath', default='output/', type=str, help='path to write output files; default is \"output/\"')
    parser.add_argument('-i', '--infiles', default=None, nargs='+', help='filename(s) to be processed')
    parser.add_argument('--ftype', default='fasta', type=str, help='file type to be processed; default is fasta')
    parser.add_argument('--source', default=None, type=str, help='data source')
    parser.add_argument('--subtype', default=None, type=str, help='subtype of virus')
    parser.add_argument('--list_viruses', default=False, action='store_true', help='list all supported viruses and exit')
    parser.add_argument('--list_datatypes', default=False,  action='store_true', help='list all supported datatypes and exit')
    parser.add_argument('--test', default=False, action='store_true', help='test run for debugging') # Remove this at some point.
    args = parser.parse_args()

    list_options(args.list_viruses, args.list_datatypes)
    assert_valid_input(**args.__dict__)

    if args.test:
        D = Dataset(**args.__dict__)
