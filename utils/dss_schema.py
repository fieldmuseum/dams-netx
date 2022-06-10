'''
Schema for EMu Media records imported via DSS to NetX
'''
import xml.etree.ElementTree as ET

def media_schema_xml() -> ET.Element:
    '''basic XML schema for NetX media record imported via DSS'''

    media_schema_xml = ET.fromstring('''
        <data>
            <AudIdentifier/>
            <irn/>
            <MulTitle/>
            <MulDescription/>
            <DetSubject_tab/>
            <AudAccessURI/>
            <AudCitation/>
            <MulMultimediaCreatorRef_tab_SummaryData/>
            <MulMultimediaCreatorRef_tab_irn/>
            <MulMultimediaCreatorRole_tab/>
            <DetMediaRightsRef_irn/>
            <DetMediaRightsRef_Summary/>
            <DetMediaRightsRef_RigType/>
            <DetMediaRightsRef_RigOwner_Summary/>
            <DetMediaRightsRef_RigOtherNumber/>
            <SecRecordStatus/>
            <SecDepartment_tab/>
            <AdmPublishWebNoPassword/>
            <AdmPublishWebPassword/>
            <MulIdentifier/>
            <AudTaxonCoverage/>
            <AudRelatedGeography/>
            <AudAssociatedSpecimen/>
            <AudAssociatedObservation/>
            <AudNumbers/>
            <AudVernacularName/>
            <AudSex/>
            <AudLifeStage/>
            <AudSubjectOrientation_tab/>
            <AudSubjectPart_tab/>
            <AudCaptureDevice/>
            <AudFundingAttribution/>
            <AdmDateInserted/>
            <AdmDateModified/>
            <AdmInsertedBy/>
            <AdmModifiedBy/>
            <RelNotes/>
            <RelParentMediaRef_SummaryData/>
            <RelParentMediaRef_AudIdentifier/>
            <RelRelatedMediaRef_tab_SummaryData/>
            <RelRelationship_tab/>
        </data>
        ''')

        # <AdmAssetSourceDAMS/>  # field not yet reportable
        # <EveEventsRef_tab_irn/>
        # <EveEventsRef_tab_GUID/>
        # <EveEventsRef_tab_SummaryData/>

    return media_schema_xml

def media_schema_json():
    '''wishful thinking'''

    media_schema_json = {
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

    return media_schema_json