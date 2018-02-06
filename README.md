# Sacra
### Sacra: a data cleaning tool designed for genomic epidemiology datasets.

Sacra is used primarily within [Nextstrain](https://github.com/nextstrain) and replaces functionality previously found in [nextstrain/fauna](https://github.com/nextstrain/fauna).
**This is under devolpment and not production ready.**


The general idea is to take possibly messy* data of varying input types (FASTA, CSV, JSON, accession numbers, titer tables), collect, clean and merge the data into a JSON output.
Sacra is idempotent, i.e. `sacra(sacra(file)) == sacra(file)`.
Uploading to a database is not part of sacra (see [nextstrain/flora](https://github.com/nextstrain/flora)).


## Requirements
* Python 2.7 (todo: make conda stuff)


## Input file types
* FASTA
* JSON
* more to come


## How To Run (general)
* move input files into `sacra/input` (e.g.)
* `python src/run.py --files INPUT_FILE_PATHS --outfile OUTPUT_JSON_PATH --pathogen PATHOGEN_NAME OTHER_ARGUMENTS`
* see `python src/run.py -h` for list of other arguments

## How To Run (testing)
* ensure you have `piglets.fasta`, `piglets_3_accessions.txt`, `mumps.vipr.fasta`, `mumps.fauna_download.fasta` in `sacra/input` (files on slack)
* `python src/run.py --files input/piglets.fasta --debug --outfile output/piglets.json --pathogen mumps --skip_entrez`
* `python src/run.py --files input/piglets_3_accessions.txt --debug --outfile output/piglets.json --pathogen mumps --skip_entrez`
* `python src/run.py --files input/mumps.vipr.fasta --debug --outfile output/piglets.json --pathogen mumps --skip_entrez --visualize_call_graph --overwrite_fasta_header alt1`
* `python src/run.py --files input/mumps.fauna_download.fasta --debug --outfile output/piglets.json --pathogen mumps --skip_entrez --overwrite_fasta_header fauna`
