# Data examples

## EMu data for determining NetX folder

### xmldata_Events.xml
An **eevents** export to find the right NetX "Events/[Event-Dept]/[Event-Title] with:
1. Directly attached Multimedia via eevents.MulMultiMediaRef_tab
2. Indirectly attached Multimedia via eevents.EveAssociatedRecordsRef_tab
    - could filter for Keys (MM irn's) where GroupType="Static" 
    - ...then retrieve those Keys' (MM irns') SecRecordStatus + SecDepartment_tab values

### xmldata_MMCat.xml
An **emultimedia** export with:
1. Multimedia data to find the right NetX "Multimedia/[Dept]" folder/s
2. Reverse-attached Catalog data to find the right NetX "Catalog/[Dept]/[Cat]" folder/s