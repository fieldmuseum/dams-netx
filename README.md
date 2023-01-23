# DAMS-NetX

Scripts for migrating media-files and corresponding data between a museum's Collections Management System (EMu) and DAMS (NetX). 

See [data/README.md](https://github.com/fieldmuseum/dams-netx/tree/main/data) for examples of how to setup NetX-EMu mappings and properties config files.

## NetX Folder structures

A given Multimedia asset will be pointed at its Netx destination folder based on these fields:
- emultimedia.SecDepartment_tab
  - 1st Security Department value is the initial NetX folder
  - Subsequent Department values are pathAdd NetX folders

## NetX Assets

### File names
- EMu MulIdentifier -> NetX "EMu File Name" (NetX attribute)
- EMu AudIdentifier -> NetX "Filename" (name of asset file in NetX)

### Attributes
- Multimedia fields from the NetX emultimedia" export are mapped in [syncedMetadata.xml](https://github.com/fieldmuseum/dams-netx/blob/main/data/config/syncedMetadata.xml)
- Reverse-attached Event fields:
  - "EveEvent" is a concatenation of:
    - eevents.EveEventNumber
    - eevents.EveTypeOfEvent
    - eevents.EveEventTitle (not all Events have EveShortName)
  - "EveEventURLs" is a concatenation of:
    - "https://pj.fieldmuseum.org/event/" + eevents.AdmGUIDValue
- Reverse-attached Catalogue fields:
  - ecatalogue.CatDepartment
  - ecatalogue.CatCatalogue


## prep_emu_media.py script - rename and copy EMu files to NetX folder structure

### How to Prep Media-Files:
1. In EMu, run the "NetX emultimedia" Multimedia export
2. `python3 prep_emu_media.py [path/to/input-emu-netx-export.xml] [path/to/output.csv] [LIVE/test]`

This script takes an emultimedia XML export and copies each record's main Multimedia file into the appropriate folder location for NetX IO to import files to NetX. The appropriate folder is defined by the SecDepartment values from EMu. The newly copied file's name is the AudIdentifier value from EMu. Once complete, NetX IO can be run in watchedFolder mode to ingest the organized, renamed files to NetX -- a prerequisite to running NetX DSS. (see example below)

#### Output:

1. Files renamed to AudIdentifier-values (with original file extension).
2. File paths defined by SecDepartment values in a folder-structure that follows the [`DEPARTMENT_CSV`](https://github.com/fieldmuseum/dams-netx/blob/main/data/config/SecDepartment_hierarchy.csv) hierarchy.
  - `DESTIN_PATH_MEDIA` and `DEPARTMENT_CSV` should be defined in your `.env` file. See [example here](https://github.com/fieldmuseum/dams-netx/blob/main/.env.example).

...like so:

    Filename | File path
    -|-
    123-abc-987-def.jpg | Multimedia/Geology/Paleobotany/


### How to Prep Media Record data:
`python3 prep_emu_xml.py [path/to/input-emu-netx-export.xml]`

This script takes the same emultimedia XML export as prep_emu_media.py, and reshapes it into 
the corresponding DSS XML input-file.

#### Output
The DSS XML input-file `dss_prepped.xml` is stored at the `DESTIN_PATH_XML` location defined in `.env`
For NetX, ingest this to the NetX front-end synced-metadata folder for the DSS autotask to pick up on its next run.


## IIIF manifest generation with mongo_to_IIIF.py
If EMu Multimedia records are indexed in a MongoDB database, this script can generate a IIIF manifest for a given EMu IRN.
The IIIF manifest outputs as a JSON file as well as to the console.  For more info about IIIF setup, see [iiif.io](https://iiif.io/get-started/how-iiif-works/)

### How to Prep
1. In the `env` file, define the following 5 MongoDB and IIIF variables:

  - **MONGO DB INFO**
    - `MONGO_DB` - add user credentials and login string to log into your MongoDB setup

  - **IIIF INFO** - default values in `.env.example` can work if you're testing locally within this repo
    - `IIIF_SCHEMA` - path to a IIIF schema json file *(e.g. "data/config/iiif_schema.json" within this repo)*
    - `IIIF_OUT_HOST` - path to the domain where an output IIIF manifest JSON file will be hosted *(e.g. while testing, could use the path to raw content in your GitHub repo: "https://raw.githubusercontent.com/[your_gh_id]/dams-netx/main")*
    - `IIIF_OUT_PATH` - writeable path to a sub-directory on that domain &/or in this repo *(e.g. "data/iiif")*
    - `IIIF_OUT_FILE` - name of the output manifest JSON file *(e.g. "manifest.json")*

2. Run the script for a given EMu irn present in MongoDB: `python3 mongo_to_IIIF.py [EMu IRN]`
  - e.g.:  `python3 mongo_to_IIIF.py 2441464`

3. Output IIIF Manifest JSON will be displayed in the console, and output to the path & file defined in your `.env`
  - e.g., see example output manifests in [data/iiif](data/iiif/)


## Related Repo's

- [`dams-beam`](https://github.com/fieldmuseum/dams-beam) - to cross-check and manage media from BEAM
- [`EMu-xml-to-json`](https://github.com/fieldmuseum/EMu-xml-to-json) - to prep EMu XML for input to `dams-netx` (among other things)