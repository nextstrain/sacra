# This will be where all(ish) arguments for sacra should live, so that class defining files only need to contain their class functions.
from dataset import Dataset
import cfg as cfg
import argparse
import os, sys

def assert_valid_input(virus, datatype, path, outpath, infile, source, subtype, **kwargs):
    '''
    Make sure that all the given arguments are valid.
    '''
    assert virus.lower() in cfg.viruses, 'Unknown virus, currently supported viruses are: %s' % (", ".join(cfg.viruses))
    assert datatype.lower() in cfg.datatypes, 'Unknown datatype, currently supported datatypes are: %s' % (", ".join(cfg.datatypes))
    assert os.path.isdir(path), 'Invalid input path: %s' % (path)
    if not os.path.isdir(outpath):
        print "Writing %s" % (path)
        os.makedirs(outpath)
    assert os.path.isfile(path+infile), 'Invalid input file: %s' % (infile)
    assert source.lower() in cfg.sources[datatype], 'Invalid source for %s data %s' % (datatype, source)
    if subtype:
        assert subtype in cfg.subtypes[virus], 'Invalid subtype %s for virus %s' % (subtype, virus)

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
    parser.add_argument('--datatype', default='sequence', type=str, help='type of data being input; default is \"sequence\", other options are \"virus\" or \"titer\"')
    parser.add_argument('-p', '--path', default='data/', type=str, help='path to input file, default is \"data/\"')
    parser.add_argument('-o', '--outpath', default='output/', type=str, help='path to write output files; default is \"output/\"')
    parser.add_argument('-i', '--infile', default=None, type=str, help='filename for file to be processed')
    parser.add_argument('--list_viruses', default=False, action='store_true', help='list all supported viruses and exit')
    parser.add_argument('--list_datatypes', default=False,  action='store_true', help='list all supported datatypes and exit')
    parser.add_argument('--source', default=None, type=str, help='data source')
    parser.add_argument('--subtype', default=None, type=str, help='subtype ')
    parser.add_argument('--test', default=False, action='store_true', help='test run for debugging') # Remove this at some point.
    parser.add_argument('--output_type', default='json', type=str, help='type of file to be written')
    args = parser.parse_args()

    if (args.infile[:len(args.path)] == args.path) and (args.path[-1] == '/'):
        args.infile = args.infile[len(args.path):]

    list_options(args.list_viruses, args.list_datatypes)
    assert_valid_input(**args.__dict__)

    if args.test:
        D = Dataset(**args.__dict__)
        testout = args.outpath + 'test.json'
        D.write(testout)
