'''
Schema for EMu Media records imported via DSS to NetX
'''
import xml.etree.ElementTree as ET

def media_schema_xml() -> ET.Element:
    '''basic XML schema for NetX media record imported via DSS'''
    
    media_schema_xml = ET.fromstring(
        text='''
        <data>
            <NetxFilename/>
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
            <DetMediaRightsRef_Rig1WebLink/>
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
            <CatCatalog/>
            <CatDepartment/>
            <EveEvent/>
            <EveEventURLs/>
            <MulOtherNumber_tab/>
            <MulOtherNumberSource_tab/>
            <ChaRepository_tab/>
            <DetSource/>
            <ChaMediaForm/>
            <DetResourceDetailDate_Created/>
            <DetResourceDetailsDate0/>
            <DetResourceDetailsDescription_tab/>
            <DetResourceType/>
            <SupIdentifier/>
            <SupHeight/>
            <SupWidth/>
            <SupFileSize/>
            <ExOb_Mul_InvNo/>
            <ExOb_Event/>
            <ExOb_Depth/>
            <ExOb_Width/>
            <ExOb_Height/>
            <ExOb_Weight/>
        </data>
        '''
        )

        # <AdmAssetSourceDAMS/>  # field not yet reportable
        # <EveEventsRef_tab_irn/>
        # <EveEventsRef_tab_GUID/>
        # <EveEventsRef_tab_SummaryData/>

    return media_schema_xml

def media_schema_json():
    '''wishful thinking'''

    media_schema_json = {
        'data': {
            'NetxFilename': None,
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
            'DetMediaRightsRef_Rig1WebLink': None,
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
            'RelRelationship_tab': None,
            'CatDepartment':None,
            'CatCatalog':None,
            'EveEvent':None,
            'EveEventURLs':None,
            'MulOtherNumber_tab':None,
            'MulOtherNumberSource_tab':None,
            'ChaRepository_tab':None,
            'DetSource':None,
            'ChaMediaForm':None,
            'DetResourceDetailDate_Created':None,
            'DetResourceDetailsDate0':None,
            'DetResourceDetailsDescription_tab':None,
            'DetResourceType':None,
            'SupIdentifier':None,
            'SupHeight':None,
            'SupWidth':None,
            'SupFileSize':None,
            'ExOb_Mul_InvNo':None,
            'ExOb_Event':None,
            'ExOb_Depth':None,
            'ExOb_Width':None,
            'ExOb_Height':None,
            'ExOb_Weight':None,
        }
    }

    return media_schema_json