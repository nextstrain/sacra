# This will be where all(ish) arguments for sacra should live, so that class defining files only need to contain their class functions.
from dataset import Dataset
import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--datatype', default='sequence', help='type of data being input; default is \"sequence\", other options are \"virus\" or \"titer\"')
    parser.add_argument('--path', default='data/', help='path to input file, default is \"data/\"')
    parser.add_argument('--outpath', default='output/', help='path to write output files; default is \"output/\"')
    parser.add_argument('-i', '--infile', default=None, help='filename for file to be processed')
    parser.add_argument('--header', default=None, type=str, nargs='*', help='specify the order of fasta header elements in a string: TODO: FIGURE OUT WHAT THE ACCEPTED HEADERS ARE. x indicates a field to skip. ex: ndxlsx for >name|date|exclude|location|state|exclude')

    args = parser.parse_args()

    D = Dataset()
    if args.datatype == 'sequence':
        fasta = args.path + args.infile
        D.read_fasta(fasta)
