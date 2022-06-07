'''Mapping EMu and NetX fields'''

def emu_netx_atoms() -> dict:
    '''
    Returns a list of dicts where keys = EMu fields 
    and values = corresponding NetX fields
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
    Returns a list of dicts where keys = EMu fields & types (atomic, ref, table) 
    and values = corresponding NetX fields
    '''

    emu_netx_tables = {
        'DetMediaRightsRef_irn':['DetMediaRightsRef', 'irn'],
        'DetMediaRightsRef_Summary':['DetMediaRightsRef', 'SummaryData'],
        'DetMediaRightsRef_RigType':['DetMediaRightsRef', 'RigType'],
        'DetMediaRightsRef_RigOwner_Summary':['DetMediaRightsRef', 'RigOwnerRef','SummaryData'],
        'DetMediaRightsRef_RigOtherNumber':['DetMediaRightsRef', 'RigOtherNumber'],
        'RelParentMediaRef_SummaryData':['RelParentMediaRef', 'SummaryData'],
        'RelParentMediaRef_AudIdentifier':['RelParentMediaRef', 'AudIdentifier'],
        'DetSubject_tab':'DetSubject_tab',
        'MulMultimediaCreatorRef_tab_SummaryData':['Creator','tuple','SummaryData'],
        'MulMultimediaCreatorRef_tab_irn':['Creator','tuple','irn'],
        'MulMultimediaCreatorRole_tab':['Creator','tuple','MulMultimediaCreatorRole'],
        'SecDepartment_tab':'SecDepartment_tab',
        'AudSubjectOrientation_tab':'AudSubjectOrientation_tab',
        'AudSubjectPart_tab':'AudSubjectPart_tab',
        'EveEventsRef_tab_irn':None,
        'EveEventsRef_tab_GUID':None,
        'EveEventsRef_tab_SummaryData':None,
        'RelRelatedMediaRef_tab_SummaryData':None,
        'RelRelationship_tab':'RelRelationship_tab'
    }

    return emu_netx_tables

    