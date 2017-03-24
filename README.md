# sacra
Sacra is designed as a replacement for [nextstrain/fauna](https://github.com/nextstrain/fauna), with the hopes of simplifying and streamlining the process of converting raw data files to usable input to [nextstrain/augur](https://github.com/nextstrain/augur).

Generally, sacra will encompass:
* Converting raw data (FASTAs, titer tables, titer long lists, and metadata) into usable inputs for augur
* Cleaning all of the read data with a comprehensive, editable suite of cleaner functions
* Allowing the user to determine if they want to upload to the fauna database or to have files made locally
* Outputting either FASTAs or JSONs
* Accessing data stored in the fauna database and downloading it to the same type of files
