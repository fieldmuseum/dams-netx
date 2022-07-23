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
`python3 prep_emu_media.py [path/to/input-emu-netx-export.xml] [path/to/output.csv] [LIVE/test]`

This script takes an emultimedia XML export and copies each file into the appropriate
folder location for NetX IO to import files to NetX. The appropriate folder is defined
by the SecDepartment values from EMu. The newly copied file's name is the AudIdentifier 
value from EMu. Once complete, NetX IO can be run in watchedFolder mode to ingest the
organized, renamed files to NetX -- a prerequisite to running NetX DSS. (see example below)

#### Output:

1. Filenames replaced with AudIdentifier
2. File paths defined by SecDepartment values in a folder-structure that follows the [`DEPARTMENT_CSV`](https://github.com/fieldmuseum/dams-netx/blob/main/data/config/SecDepartment_hierarchy.csv) hierarchy
    - `DESTIN_PATH_MEDIA` and `DEPARTMENT_CSV` should be defined in your `.env` file. See [example here](https://github.com/fieldmuseum/dams-netx/blob/main/.env.example).

...like so:

  | Filename | File path |
  |---|---|
  | 123-abc-987-def.jpg | Multimedia/Geology/Paleobotany/ |


### How to Prep Media Record data:
`python3 prep_emu_xml.py [path/to/input-emu-netx-export.xml]`

This script takes the same emultimedia XML export as prep_emu_media.py, and reshapes it into 
the corresponding DSS XML input-file.

#### Output
The DSS XML input-file `dss_prepped.xml` is stored at the `DESTIN_PATH_XML` location defined in `.env`
For NetX, ingest this to the NetX front-end synced-metadata folder for the DSS autotask to pick up on its next run.



## Related Repo's

- [`dams-beam`](https://github.com/fieldmuseum/dams-beam) - to cross-check and manage media from BEAM
- [`EMu-xml-to-json`](https://github.com/fieldmuseum/EMu-xml-to-json) - to prep EMu XML for input to `dams-netx` (among other things)
