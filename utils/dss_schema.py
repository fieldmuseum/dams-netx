'''
Schema for EMu Media records imported via DSS to NetX
'''

def media_schema():
    
    media_schema = {
        'data': {
            'AudIdentifier': None,
            'irn': None,
            'MulTitle': None,
            'MulDescription': None,
            'DetSubject_tab': None,
            'AudAssociatedSpecimen': None,
            'AudAccessURI': None,
            'AudCitation': None,
            'MulCreator_tab': None,
            'MulMultimediaCreatorRef_tab_SummaryData': None,
            'MulMultimediaCreatorRef_tab_irn': None,
            'MulMultimediaCreatorRole_tab': None,
            'DetMediaRightsRef_irn': None,
            'DetMediaRightsRef_Summary': None,
            'DetMediaRightsRef_RigType': None,
            'DetMediaRightsRef_RigOwner_Summary': None,
            'DetMediaRightsRef_RigOtherNumber': None,
            'SecRecordStatus': None,
            'SecDepartment_tab': None,
            'AdmPublishWebNoPassword': None,
            'AdmPublishWebPassword': None,
            'AdmAssetSourceDAMS': None,
            'AudTaxonCoverage': None,
            'AudRelatedGeography': None,
            'AudAssociatedSpecimen': None,
            'AudAssociatedObservations': None,
            'AudNumbers': None,
            'AudVernacularName': None,
            'AudSex': None,
            'AudLifeStage': None,
            'AudSubjectOrientation_tab': None,
            'AudSubjectPart_tab': None,
            'AudCaptureDevice': None,
            'AudFundingAttribution': None,
            'AudAccessURI': None,
            'DetMediaRightsRef_RigType': None,
            'DetMediaRightsRef_RigOtherNumber': None,
            'EveEventsRef_tab_irn': None,
            'EveEventsRef_tab_GUID': None,
            'EveEventsRef_tab_SummaryData': None,
            'AdmDateInserted': None,
            'AdmDateModified': None,
            'AdmInsertedBy': None,
            'AdmModifiedBy': None,
            'RelChildMediaRef_tab_SummaryData': None,
            'RelNotes': None,
            'RelParentMediaRef_SummaryData': None,
            'RelRelatedMediaRef_tab_SummaryData': None,
            'RelRelationship_tab': None
        }
    }

    return media_schema