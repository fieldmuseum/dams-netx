'''Mapping EMu and NetX fields'''

import csv
import os
import re
from xml.etree import ElementTree as ET

def emu_netx_atoms() -> dict:
    '''
    Returns a dict where keys = corresponding NetX fields
    and values = EMu fields
    '''

    atoms = {
        'AudIdentifier':'AudIdentifier',
        'irn':'irn',
        'MulTitle':'MulTitle',
        'MulDescription':'MulDescription',
        'AudAccessURI':'AudAccessURI',
        'AudCitation':'AudCitation',
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
        'AdmDateInserted':'AdmDateInserted',
        'AdmDateModified':'AdmDateModified',
        'AdmInsertedBy':'AdmInsertedBy',
        'AdmModifiedBy':'AdmModifiedBy',
        'RelNotes':'RelNotes',
        'MulIdentifier':'MulIdentifier',
        'DetSource':'DetSource',
        'ChaMediaForm':'ChaMediaForm',
        'DetResourceType':'DetResourceType',
    }

    return atoms


def emu_netx_tables() -> dict:
    '''
    Returns a dict where keys = correspinding NetX fields
    and values = EMu table-field column names (e.g. DetSubject_Tab)
    '''

    tables = {
        'DetSubject_tab':'DetSubject_tab',
        'SecDepartment_tab':'SecDepartment_tab',
        'AudSubjectOrientation_tab':'AudSubjectOrientation_tab',
        'AudSubjectPart_tab':'AudSubjectPart_tab',
        'ChaRepository_tab':'ChaRepository_tab'
    }

    return tables


def emu_netx_refs() -> dict:
    '''
    Returns a dict where keys = corresponding NetX fields
    and values = list of EMu "Ref" attachment fields and pull-thru fields
    If a double-nested field is included, 
      '.'-delimit as [link column].[pull-through] in a single string
      e.g. - For DetMediaRightsRef:  RigOwnershipRef_tab.SummaryData
    '''

    refs = {
        'DetMediaRightsRef_irn':['DetMediaRightsRef', 'irn'],
        'DetMediaRightsRef_Summary':['DetMediaRightsRef', 'SummaryData'],
        'DetMediaRightsRef_RigType':['DetMediaRightsRef', 'RigType'],
        'DetMediaRightsRef_RigOwner_Summary':[
            'DetMediaRightsRef', 'RigOwnershipRef_tab.SummaryData'
            ],
        # try RigOwnershipRef_tab/SummaryData ?
        'DetMediaRightsRef_RigOtherNumber':['DetMediaRightsRef', 'RigOtherNumber'],
        'DetMediaRightsRef_Rig1WebLink':['DetMediaRightsRef', 'Rig1WebLink'],
        'RelParentMediaRef_SummaryData':['RelParentMediaRef', 'SummaryData'],
        'RelParentMediaRef_AudIdentifier':['RelParentMediaRef', 'AudIdentifier']
    }

    return refs


def emu_netx_groups_or_reftabs() -> dict:
    '''
    Returns a dict where keys = corresponding NetX fields
    and values = lists of EMu XML Group names and nested EMu fields  
    
    If groups includes attachment-fields, only the pull-through fields are listed.
    (e.g. only "SummaryData", not "MulMultimediaCreatorRef_tab.SummaryData")
    
    If a double-nested field is included,
      '.'-delimit as [link column].[pull-through] in a single string
      e.g. - For ExOb_Event (StaEventRef):  StaEventRef.SummaryData
    
    If a NetX field may pull from multiple EMu groups, list the group-names in order of priority.
    e.g. - For ExOb_Event, the Ex.Ob's Install-tab media ('InsMultimediaRef_tab') 
    takes priority over main 'Multimedia-tab' media ('MulMultiMediaRef_tab')
    '''

    groups_or_reftabs = {
        'MulMultimediaCreatorRef_tab_SummaryData':['Creator','SummaryData'],
        'MulMultimediaCreatorRef_tab_irn':['Creator','irn'],
        'MulMultimediaCreatorRole_tab':['Creator','MulMultimediaCreatorRole'],
        'MulOtherNumber_tab':['OtherNumbers','MulOtherNumber'],
        'MulOtherNumberSource_tab':['OtherNumbers','MulOtherNumberSource'],
        'RelRelatedMediaRef_tab_SummaryData':['RelatedMedia','SummaryData'],
        'RelRelationship_tab':['RelatedMedia','RelRelationship'],
        'CatDepartment':['MulMultiMediaRef_tab','CatDepartment'], # make unique list
        'CatCatalog':['MulMultiMediaRef_tab','CatCatalog'], # make unique list
        'DetResourceDetailsDate0': ['Dates', 'DetResourceDetailsDate'],
        'DetResourceDetailsDescription_tab': ['Dates', 'DetResourceDetailsDescription'],
        'SupIdentifier': ['Supplementary', 'SupIdentifier'],
        'SupHeight': ['Supplementary', 'SupHeight'],
        'SupWidth': ['Supplementary', 'SupWidth'],
        'SupFileSize': ['Supplementary', 'SupFileSize'],
        'ExOb_Mul_InvNo':[
            ['InsMultimediaRef_tab', 'MulMultiMediaRef_tab'],
            'StaEventCatalogueNumber'
            ],
        'ExOb_Event':[
            ['InsMultimediaRef_tab', 'MulMultiMediaRef_tab'],
            'StaEventRef.SummaryData'
            ],  # Double-nested reverse-attachment...
        'ExOb_Depth':['InsMultimediaRef_tab','MeaConfirmedDepth'],
        'ExOb_Width':['InsMultimediaRef_tab','MeaConfirmedWidth'],
        'ExOb_Height':['InsMultimediaRef_tab','MeaConfirmedHeight'],
        'ExOb_Weight':['InsMultimediaRef_tab','MeaConfirmedWeight']
    }

    return groups_or_reftabs



# def emu_netx_conditional_groups() -> dict:
#     '''
#     Returns a list of dicts that define if/then conditions:
#     If a given EMu XML group or table field's value meets defined "if" criteria,
#     then the given NetX "then_field" will be set to the defined then_value.

#     Either "then_value_dynamic" (to set NetX to the value in another EMu field)
#     or "then_value_static" (to set NetX to a static value in the dictionary)
#     should be used for a given field's condition -- not both.
#     '''

#     emu_netx_conditional_groups = {
#         'DetResourceDetailsDate0': ['Dates', 'DetResourceDetailsDate'],
#         'DetResourceDetailDate_Created': ['Dates', 'DetResourceDetailsDescription']
#         }

#     return emu_netx_conditional_groups

def emu_netx_ref_concatenate() -> dict:
    '''
    Returns a list of dicts where keys = corresponding NetX fields
    and values = list of EMu Ref fields to concatenate.
    Values will be joined in the order they are listed, delimited by pipes: "a | b | c"
    '''
    ref_concatenate = {
        'EveEvent':['MulMultiMediaRef_tab',['EveEventNumber','EveTypeOfEvent','EveEventTitle']],
        'EveEventURLs':['MulMultiMediaRef_tab','AdmGUIDValue']
    }

    return ref_concatenate


def get_folder_hierarchy(department_raw:str, dept_csv:str) -> str:
    '''
    Get the appropriate parent-folder value for a given SecDepartment value
    '''
    # dept_csv = config('DEPARTMENT_CSV')
    dept_folders = []
    with open(dept_csv, encoding='utf-8', mode = 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for r in reader:
            dept_folders.append(r)

    # make lists of level_1 & level_2 values
    # NOTE - NOT unique lists; a value's index will be used to get the corresponding parent
    dept_emu = [row['emu'] for row in dept_folders]
    # for row in dept_folders:
    #     dept_emu.append(row['emu'])

    dept_level_1 = [row['netx_level_1'] for row in dept_folders]
    # for row in dept_folders:
    #     dept_level_1.append(row['netx_level_1'])

    dept_level_2 = [row['netx_level_2'] for row in dept_folders]
    # for row in dept_folders:
    #     dept_level_2.append(row['netx_level_2'])

    department = department_raw.strip()

    if department in dept_level_2:
        # lookup level_1 value at same index for level_2 key/value
        parent = dept_level_1[dept_level_2.index(department)]
        return parent + '/' + department + '/'

    elif department in dept_emu:
        # return department + '/'
        return dept_level_1[dept_emu.index(department)] + '/'

    else:
        print(f"No matching folder hierarchy value for {department}")
        return None


def get_emu_netx_conditions(conditions_csv:str) -> str:
    '''
    Returns a list of conditions for conditionally mapped EMu/NetX fields.
    '''
    # dept_csv = config('CONDITIONS_CSV')
    conditions = []
    if os.path.isfile(conditions_csv):
        with open(conditions_csv, encoding='utf-8', mode = 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for r in reader:
                if r not in conditions:
                    conditions.append(r)

    else:
        print(f'No conditions_csv found for CONDITIONS_CSV value: {conditions_csv}')

    # dept_emu = []
    # for row in dept_folders: dept_emu.append(row['emu'])

    return conditions


def get_condition_field_list(conditions:list):
    '''Returns a list of 'then_field's where output DSS field is conditionally mapped.'''

    then_field_list = []

    gen = (item['then_field'] for item in conditions)
    for field in gen:
        if field not in then_field_list:
            then_field_list.append(field)

    return then_field_list


def get_dss_xml(dss_xml_path:dict) -> dict:
    '''Convert syncedMetadata.xml DSS config to dict of {emu_field:netx_field}'''

    if os.path.isfile(dss_xml_path):
        # with open(dss_xml_path, encoding='utf-8', mode = 'r') as xmlfile:

        netx_emu_tree = ET.parse(dss_xml_path)
        netx_emu_root = netx_emu_tree.getroot()

        destination = []
        source = []

        for child in netx_emu_root:
            if child.attrib['name'] == 'XML Metadata sync':
                for grandkid in child:
                    if grandkid.tag == "source":
                        source = grandkid
                    else:
                        for greatgrand in grandkid:
                            if greatgrand.tag == "records":
                                destination = greatgrand

        for child in destination:
            if child.tag == 'records':
                records = child

        netx_emu_map = {}

        for emu_field in source:
            for records in destination:
                for netx_field in records:
                    if emu_field.attrib['name'] == netx_field.attrib['field']:
                        emu_field_name = emu_field.attrib['column']
                        netx_field_name = netx_field.attrib['attribute']
                        # emu_field.set('netx', netx_field.attrib['attribute'])
                        netx_emu_map[emu_field_name] = netx_field_name

    else: print(f'check dss_xml_path -- {dss_xml_path}')

    print(f'netx_emu_map = {netx_emu_map}')

    return netx_emu_map


def clean_emu_filename(emu_filename:str) -> str:
    '''Given an EMu filename, return cleaned EMu filename without spaces/special characters'''

    clean_ext = re.sub(r'(.+)(\..+$)', r'\g<2>', emu_filename)

    clean_name = re.sub(r'[\'!@#\$%\^\*\?<>%"\{\}/\\&\.,\:;\s+\(\)\[\]\-]', '_', emu_filename)
    clean_name = re.sub(r'_+', '_', clean_name)
    clean_name = re.sub(r'(.+)(_.+$)', r'\g<1>' + clean_ext, clean_name)
    # (.+(_.+)*)(_)(.+$)', r'\g<1>.\g<3>', clean_name)

    return clean_name


def emu_iiif_metadata_labels() -> dict:
    '''
    Returns a dict where keys = EMu columns
    and values = corresponding IIIF Metadata Labels
    '''

    metadata_labels = {
            'MulTitle':'Title',
            'MulDescription':'Description',
            'AudCitation':'Citation',
            'AudTaxonCoverage':'Taxon Coverage',
            'AudRelatedGeography':'Related Geography',
            'AudAssociatedSpecimen':'Associated Specimen',
            'AudAssociatedObservations':'Associated Observations',
            'AudNumbers':'Catalog Numbers',
            'AudVernacularName':'Vernacular Name',
            'AudSex':'Sex',
            'AudLifeStage':'Life Stage',
            'AudCaptureDevice':'Capture-Device',
            'AudFundingAttribution':'Funding Attribution',
            # 'AdmDateInserted':'Date Inserted',
            # 'AdmDateModified':'Date Modified',
            'RelNotes':'Notes',
            'MulIdentifier':'Filename',
            'DetSource':'Source',
            'ChaMediaForm':'Media Form',
            # 'DetResourceType':'Resource Type',
            # 'DetResourceSubtype':'Resource Subtype',
            'AudIdentifier':'Identifier',
            'AudAccessURI':'Access URI'
            # 'irn':'FMNH EMu irn'
    }

    return metadata_labels


def get_emu_netx_map(config):
    '''Use NetX syncedMetadata.xml to setup EMu/NetX mapping dictionary'''

    dss_xml = config['DSS_XML']

    emu_netx_fields_raw = ET.parse(dss_xml)
    emu_netx_fields = emu_netx_fields_raw.getroot()
    emu_dss = emu_netx_fields.find(path=".//*[@name='XML Metadata sync']")
    emu_fields = [emu for emu in emu_dss if 'column' in emu.attrib]  # .findall(path='.//field')]
    netx_fields = [netx for netx in emu_dss if 'attribute' in netx.attrib ]
    # emu_dss.findall(path='.//map')]
    # field_map = list(zip(emu_fields[1:], netx_fields))  # quick/dirty version
    field_map = []
    for emu_field in emu_fields:
        for netx_field in netx_fields:
            if emu_field.attrib['name'] == netx_field.attrib['field']:
                emu_netx_match = {
                    netx_field.attrib['attribute'] : emu_field.attrib['column']
                }
                field_map.append(emu_netx_match)

    return field_map
