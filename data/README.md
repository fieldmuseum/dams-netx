# Data examples

## EMu data for determining NetX folder

### xml_good_examples
These consist of the full folder structure for 3 EMu XML exports on 2022-8-11.
Each XML files includes 10 corresponding multimedia records.

- "NetX_emultimedia" includes all mapped emultimedia fields, and is the main input for `prep_emu_media.py`.
  - The SecDepartment values in this XML file determine an asset's NetX folders.

- "NetX_mm_catalogue" includes 2 fields pulled from any reverse-attached ecatalogue records.
- "NetX_mm_events" includes 5 fields pulled from any reverse-attached event records.

### xml_bad_examples
These include a variety of badly-formed individual files, as well as bad folder-structures missing export-files.