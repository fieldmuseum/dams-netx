# DAMS-NetX

A repo for documentation and scripts for migrating and maintaining media and workflows related to NetX.

NetX folder structures:

A given Multimedia asset could be pointed at its Netx destination folder based on these fields:
- Multimedia fields:
  - emultimedia.SecDepartment_tab
  - emultimedia.SecRecordStatus
- Reverse-attached Event fields:
  - eevents.SecDepartment_tab
  - eevents.EveEventTitle
- Reverse-attached Catalogue fields:
  - ecatalogue.CatDepartment
  - ecatalogue.CatCatalogue

system | folder level-1 | folder level-2
-|-|-
NetX |  "**Multimedia**" | [MM-Department folder]
EMu | [emultimedia module] | emultimedia.SecDepartment_tab 

system | folder level-1 | folder level-2 | folder level-3
-|-|-|-
NetX | "**Events**" | [Event-Department folder] | [Event Title folder]
EMu | [eevents module] | eevents.SecDepartment_tab | eevents.EveEventTitle

system | folder level-1 | folder level-2 | folder level-3
-|-|-|-
NetX | "**Catalogue**" | [Cat-Department folder] | [Catalogue folder]
EMu | [ecatalogue module] | ecatalogue.CatDepartment | ecatalogue.CatCatalogue

## NetX pathMove prep script - copy EMu files to NetX pathMove folder structure

### How to Prep Media-Files:
`python3 pathmove_prep.py [path/to/input-emu-netx-export.xml] [path/to/output.csv] [LIVE/test]`

This script takes an emultimedia XML export and copies each file into the appropriate
folder location for NetX pathMove. The newly copied file has a new filename, which
is the AudIdentifier value from EMu. The output is a CSV of each multimedia record, with
the fields, `File`, NetX `pathMove` and `AudIdentifier`. The `pathMove` value 
is the filepath of the media that NetX requires for ingestion. (see example below)

#### Output:

1. Renamed files referenced in the input-XML, saved to the `DESTIN_PATH` directory in a folder-structure that follows the [`DEPARTMENT_CSV`](https://github.com/fieldmuseum/dams-netx/blob/main/data/config/SecDepartment_hierarchy.csv) hierarchy
    - `DESTIN_PATH` and `DEPARTMENT_CSV` should be defined in your `.env` file. See [example here](https://github.com/fieldmuseum/dams-netx/blob/main/.env.example).
2. A CSV formatted like so:

    File | pathMove (output path where renamed file should go in NetX) | Identifier
    -|-|-
    123-abc-987-def.jpg | Multimedia/Paleobotany/ | 123-abc-987-def


### How to Prep Media Record data:
`python3 emu_xml_reshape.py [path/to/input-emu-netx-export.xml]`

This script takes the same emultimedia XML export as pathmove_prep.py, and reshapes it into 
the corresponding DSS XML input-file.

#### Output
The DSS XML input-file `dss_prepped.xml` is stored at the `XML_OUT_PATH` defined in `.env`
For NetX, ingest this to the NetX front-end synced-metadata folder for the DSS autotask to pick up on its next run.



## Related Repo's

- [`dams-beam`](https://github.com/fieldmuseum/dams-beam) - to cross-check and manage media from BEAM
- [`EMu-xml-to-json`](https://github.com/fieldmuseum/EMu-xml-to-json) - to prep EMu XML for input to `dams-netx` (among other things)
