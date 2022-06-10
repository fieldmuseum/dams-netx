'''Mapping EMu and NetX fields'''

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
            'MulIdentifier':'MulIdentifier'
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
        'AudSubjectPart_tab':'AudSubjectPart_tab'
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
        'DetMediaRightsRef_RigOwner_Summary':['DetMediaRightsRef', 'RigOwnershipRef_tab.SummaryData'],
        'DetMediaRightsRef_RigOtherNumber':['DetMediaRightsRef', 'RigOtherNumber'],
        'RelParentMediaRef_SummaryData':['RelParentMediaRef', 'SummaryData'],
        'RelParentMediaRef_AudIdentifier':['RelParentMediaRef', 'AudIdentifier'],
    }

    return emu_netx_refs


def emu_netx_groups() -> dict:
    '''
    Returns a list of dicts where keys = corresponding NetX fields
    and values = lists of Group names and nested EMu fields  
    If groups includes attachment-fields, only the pull-through fields are listed.
    (e.g. only "SummaryData", not "MulMultimediaCreatorRef_tab.SummaryData")
    '''

    emu_netx_groups = {
        'MulMultimediaCreatorRef_tab_SummaryData':['Creator','SummaryData'],
        'MulMultimediaCreatorRef_tab_irn':['Creator','irn'],
        'MulMultimediaCreatorRole_tab':['Creator','MulMultimediaCreatorRole']
    }

    return emu_netx_groups

    