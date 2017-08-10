# sacra
Sacra is designed as a replacement for [nextstrain/fauna](https://github.com/nextstrain/fauna), with the hopes of simplifying and streamlining the process of converting raw data files to usable input to [nextstrain/augur](https://github.com/nextstrain/augur).

Generally, sacra will encompass:
* Converting raw data (FASTAs, titer tables, titer long lists, and metadata) into usable inputs for augur
* Cleaning all of the read data with a comprehensive, editable suite of cleaner functions
* Allowing the user to determine if they want to upload to the fauna database or to have files made locally
* Outputting either FASTAs or JSONs
* Accessing data stored in the fauna database and downloading it to the same type of files

## Requirements
Python 2.7

## Acceptable file types
Sequence data:
* fasta
* fasta + tsv
* json
* sacra output json

Titer data:

## How to run

With a file named `gisaid_test.fasta` in the `data/` directory, a test run of sacra can be done by running:
`python src/run.py --infiles gisaid_test.fasta --source GISAID --test`
This will write a JSON to the `output` directory.

If uploading multiple files is necessary, the call can be altered to: `python src/run.py --infiles split_file_1.fasta split_file_2.fasta --source gisaid --test`.

## Explanation of options
- `-v`, `--virus`:
  - Virus species that will be processed in the dataset run. To avoid errors, this should be present in `src/cfg.py`.
  - _Default:_ `seasonal_flu`
- `-d`, `--datatype`:
  - Type of data that will be processed (i.e. sequence, titer, epi). To avoid errors, this should be present in `src/cfg.py`
  - _Default:_ `sequence`
- `-p`, `--path`:
  - Path to directory containing input files.
  - _Default:_ `data/`
- `-o`, `--outpath`:
  - Path to directory where output files will be written.
  - _Default:_ `output/`
- `-i`, `--infiles`:
  - Filenames that will be handled in a single Sacra run. To avoid errors, make sure that all listed files are of the same filetype (see below).
- `--ftype`:
  - Type of file to be processed. Supported filetypes need to be listed in `src/cfg.py`.
  - _Options:_ `fasta`
  - _Default:_ `fasta`
- `--source`:
  - Source from which the data came. Used in `src/cfg.py` to specify parameters specific to a given source (i.e. order of metadata in a FASTA header)
- `--subtype`:
  - Subtype of a given virus, if known.
-  `--list_viruses`:
  - Lists all supported viruses and exits.
- `--list_datatypes`:
  - Lists all supported datatypes and exits.

# Datasets


# `cfg.py` and `cleaning_functions.py`
