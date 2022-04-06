# DAMS-NetX

A repo for documentation and scripts for migrating and maintaining media and workflows related to NetX.

NetX folder structures:
Note - the top level 'Active/Restricted' folder might be removed, but for testing/for now:

A given Multimedia asset could be pointed at its Netx destination folder based on these fields:
- emultimedia.SecRecordStatus
  - Multimedia fields:
    - emultimedia.SecDepartment_tab
    - emultimedia.SecRecordStatus
  - Reverse-attached Event fields:
    - eevents.SecDepartment_tab
    - eevents.EveEventTitle
  - Reverse-attached Catalogue fields:
    - ecatalogue.CatDepartment
    - ecatalogue.CatCatalogue

system | folder level-1 | folder level-2 | folder level-3
-|-|-|-
NetX | [Active/Restricted] | "**Multimedia**" | [MM-Department folder]
EMu | [emultimedia.SecRecordStatus] | [emultimedia module] | emultimedia.SecDepartment_tab 

system | folder level-1 | folder level-2 | folder level-3 | folder level-4
-|-|-|-|-
NetX | [Active/Restricted] | "**Events**" | [Event-Department folder] | [Event Title folder]
EMu | [emultimedia.SecRecordStatus] | [eevents module] | eevents.SecDepartment_tab | eevents.EveEventTitle

system | folder level-1 | folder level-2 | folder level-3 | folder level-4
-|-|-|-|-
NetX | [Active/Restricted] | "**Catalogue**" | [Cat-Department folder] | [Catalogue folder]
EMu | [emultimedia.SecRecordStatus] | [ecatalogue module] | ecatalogue.CatDepartment | ecatalogue.CatCatalogue



