# Data examples


## xml_good_examples
These consist of the full folder structure for 3 EMu XML exports on 2022-8-11.
Each XML files includes 10 corresponding multimedia records.

- "NetX_emultimedia" includes all mapped emultimedia fields, and is the main input for `prep_emu_media.py`.
  - The SecDepartment values in this XML file determine an asset's NetX folders.

- "NetX_mm_catalogue" includes 2 fields pulled from any reverse-attached ecatalogue records.
- "NetX_mm_events" includes 5 fields pulled from any reverse-attached event records.


## xml_bad_examples
These include a variety of badly-formed individual files, as well as bad folder-structures and missing export-files.


## config
This folder includes example setup-files for **dams-netx** scripts, **NetX I/O** and **NetX DSS**.
- `SecDepartment_hierarchy.csv` - should be referenced by prep-scripts and variables in this repo's `.env` 
- `netxio.properties` example - an example of the proprties-file recommended for running NetX I/O via the command line interface (CLI).
- `syncedMetadata` XML example - an example of the mapping file required for NetX DSS.