'''Mapping EMu and NetX fields'''

import csv

def emu_netx_atoms() -> dict:
    '''
    Returns a list of dicts where keys = corresponding NetX fields
    and values = EMu fields
    '''

    emu_netx_atoms = {
            'AudIdentifier':'AudIdentifier',
            'irn':'irn',
            'MulTitle':'MulTitle',
            'MulDescription':'MulDescription',
            'AudAssociatedSpecimen':'AudAssociatedSpecimen',
            'AudAccessURI':'AudAccessURI',
            'AudCitation':'AudCitation',
            # 'DetMediaRightsRef_irn',
            # 'DetMediaRightsRef_Summary',
            # 'DetMediaRightsRef_RigType',
            # 'DetMediaRightsRef_RigOwner_Summary',
            # 'DetMediaRightsRef_RigOtherNumber',
            'SecRecordStatus':'SecRecordStatus',
            'AdmPublishWebNoPassword':'AdmPublishWebNoPassword',
            'AdmPublishWebPassword':'AdmPublishWebPassword',
            'AdmAssetSourceDAMS':'AdmAssetSourceDAMS',
            'AudTaxonCoverage':'AudTaxonCoverage',
            'AudRelatedGeography':'AudRelatedGeography',
            'AudAssociatedSpecimen':'AudAssociatedSpecimen',
            'AudAssociatedObservations':'AudAssociatedObservations',
            'AudNumbers':'AudNumbers',
            'AudVernacularName':'AudVernacularName',
            'AudSex':'AudSex',
            'AudLifeStage':'AudLifeStage',
            'AudCaptureDevice':'AudCaptureDevice',
            'AudFundingAttribution':'AudFundingAttribution',
            'AudAccessURI':'AudAccessURI',
            'AdmDateInserted':'AdmDateInserted',
            'AdmDateModified':'AdmDateModified',
            'AdmInsertedBy':'AdmInsertedBy',
            'AdmModifiedBy':'AdmModifiedBy',
            'RelNotes':'RelNotes',
            'MulIdentifier':'MulIdentifier',
            'DetSource':'DetSource'
            # 'RelParentMediaRef_SummaryData'
    }

    return emu_netx_atoms


def emu_netx_tables() -> dict:
    '''
    Returns a list of dicts where keys = correspinding NetX fields
    and values = EMu table-field column names (e.g. DetSubject_Tab)
    '''

    emu_netx_tables = {
        'DetSubject_tab':'DetSubject_tab',
        'SecDepartment_tab':'SecDepartment_tab',
        'AudSubjectOrientation_tab':'AudSubjectOrientation_tab',
        'AudSubjectPart_tab':'AudSubjectPart_tab',
        'ChaRepository_tab':'ChaRepository_tab'
        # 'DetMediaRightsRef_irn':['DetMediaRightsRef', 'irn'],
        # 'DetMediaRightsRef_Summary':['DetMediaRightsRef', 'SummaryData'],
        # 'DetMediaRightsRef_RigType':['DetMediaRightsRef', 'RigType'],
        # 'DetMediaRightsRef_RigOwner_Summary':['DetMediaRightsRef', 'RigOwnerRef','SummaryData'],
        # 'DetMediaRightsRef_RigOtherNumber':['DetMediaRightsRef', 'RigOtherNumber'],
        # 'RelParentMediaRef_SummaryData':['RelParentMediaRef', 'SummaryData'],
        # 'RelParentMediaRef_AudIdentifier':['RelParentMediaRef', 'AudIdentifier'],
        # 'MulMultimediaCreatorRef_tab_SummaryData':['Creator','tuple','SummaryData'],
        # 'MulMultimediaCreatorRef_tab_irn':['Creator','tuple','irn'],
        # 'MulMultimediaCreatorRole_tab':['Creator','tuple','MulMultimediaCreatorRole'],
        # 'EveEventsRef_tab_irn':None,
        # 'EveEventsRef_tab_GUID':None,
        # 'EveEventsRef_tab_SummaryData':None,
        # 'RelRelatedMediaRef_tab_SummaryData':None,
        # 'RelRelationship_tab':'RelRelationship_tab'
    }

    return emu_netx_tables


def emu_netx_refs() -> dict:
    '''
    Returns a list of dicts where keys = corresponding NetX fields
    and values = list of EMu "Ref" attachment fields and pull-thru fields
    If a double-nested field is included, '.'-delimit as [link column].[pull-through] in a single string
    e.g. - For DetMediaRightsRef:  RigOwnershipRef_tab.SummaryData
    '''

    emu_netx_refs = {
        'DetMediaRightsRef_irn':['DetMediaRightsRef', 'irn'],
        'DetMediaRightsRef_Summary':['DetMediaRightsRef', 'SummaryData'],
        'DetMediaRightsRef_RigType':['DetMediaRightsRef', 'RigType'],
        'DetMediaRightsRef_RigOwner_Summary':['DetMediaRightsRef', 'RigOwnershipRef_tab.SummaryData'],  # try RigOwnershipRef_tab/SummaryData ?
        'DetMediaRightsRef_RigOtherNumber':['DetMediaRightsRef', 'RigOtherNumber'],
        'RelParentMediaRef_SummaryData':['RelParentMediaRef', 'SummaryData'],
        'RelParentMediaRef_AudIdentifier':['RelParentMediaRef', 'AudIdentifier']
    }

    return emu_netx_refs


def emu_netx_groups_or_reftabs() -> dict:
    '''
    Returns a list of dicts where keys = corresponding NetX fields
    and values = lists of Group names and nested EMu fields  
    If groups includes attachment-fields, only the pull-through fields are listed.
    (e.g. only "SummaryData", not "MulMultimediaCreatorRef_tab.SummaryData")
    '''

    emu_netx_groups_or_reftabs = {
        'MulMultimediaCreatorRef_tab_SummaryData':['Creator','SummaryData'],
        'MulMultimediaCreatorRef_tab_irn':['Creator','irn'],
        'MulMultimediaCreatorRole_tab':['Creator','MulMultimediaCreatorRole'],
        'MulOtherNumber_tab':['OtherNumbers','MulOtherNumber'],
        'MulOtherNumberSource_tab':['OtherNumbers','MulOtherNumberSource'],
        'RelRelatedMediaRef_tab_SummaryData':['RelatedMedia','SummaryData'],
        'RelRelationship_tab':['RelatedMedia','RelRelationship'],
        'CatDepartment':['MulMultiMediaRef_tab','CatDepartment'], # make unique list
        'CatCatalog':['MulMultiMediaRef_tab','CatCatalog'] # make unique list
    }

    return emu_netx_groups_or_reftabs


def emu_netx_ref_concatenate() -> dict:
    '''
    Returns a list of dicts where keys = corresponding NetX fields
    and values = list of EMu Ref fields to concatenate.
    Values will be joined in the order they are listed, delimited by pipes: "a | b | c"
    '''
    emu_netx_ref_concatenate = {
        'EveEvent':['MulMultiMediaRef_tab',['EveEventNumber','EveTypeOfEvent','EveEventTitle']],
        'EveEventURLs':['MulMultiMediaRef_tab','AdmGUIDValue']
    }

    return emu_netx_ref_concatenate


def get_folder_hierarchy(department_raw:str, dept_csv:str) -> str:
    '''
    Get the appropriate parent-folder value for a given SecDepartment value
    '''
    # dept_csv = config('DEPARTMENT_CSV')
    dept_folders = []
    with open(dept_csv, encoding='utf-8', mode = 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for r in reader: dept_folders.append(r)

    # make lists of level_1 & level_2 values
    # NOTE - NOT unique lists; a value's index will be used to get the corresponding parent
    dept_emu = []
    for row in dept_folders: dept_emu.append(row['emu'])

    dept_level_1 = []
    for row in dept_folders: dept_level_1.append(row['netx_level_1'])

    dept_level_2 = []
    for row in dept_folders: dept_level_2.append(row['netx_level_2'])

    department = department_raw.strip()

    if department in dept_level_2:
        # lookup level_1 value at same index for level_2 key/value
        parent = dept_level_1[dept_level_2.index(department)]
        return parent + '/' + department + '/'
    
    else: 
        # return department + '/'
        return dept_level_1[dept_emu.index(department)] + '/'
