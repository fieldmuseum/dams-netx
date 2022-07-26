'''
Parse EMu XML to DAMS-ready XML
2022-Jun; FMNH, based on EMu-xml-to-json convert_xml.py
'''

import xml.etree.ElementTree as ET
import os, re, sys
import glob
from decouple import config
import utils.dss_schema as dss_schema
import utils.xml_tools as xml_tools
import utils.emu_netx_map as emu_netx


def parse_emu_to_dss(emu_record: ET.Element, mm_event: ET.Element, mm_catalog: ET.Element) -> ET.Element:
    '''Parse exported EMu records to DSS-schema records'''

    print(emu_record.find('irn').text)

    # Setup record's DSS fields
    prepped_record = dss_schema.media_schema_xml()

    # Add NetxFilename field as key / remap AudIdentifier
    file_ext = re.sub(r'(.*)(\..{2,4}$)', r'\g<2>', emu_record.find('MulIdentifier').text)
    prepped_record.find('NetxFilename').text = emu_record.find('AudIdentifier').text + file_ext


    # Populate DSS fields for atomic EMu fields:
    atomic_fields = emu_netx.emu_netx_atoms()

    for key, value in atomic_fields.items():
        if value is not None and emu_record.find(value) is not None:
            prepped_record.find(key).text = emu_record.find(value).text

            if key == "AudAssociatedSpecimen" and prepped_record.find(key).text is not None:
                prepped_record.find(key).text = 'https://db.fieldmuseum.org/' + prepped_record.find(key).text


    # Populate table-fields
    table_fields = emu_netx.emu_netx_tables()

    for key, value in table_fields.items():
        if type(value) == list:
            print('figure this out')
            
        elif value is not None and emu_record.find(value) is not None:
            # This pulls the concatenated value from convert_linebreaks_to_commas()
            prepped_record.find(key).text = emu_record.find(value).text
    

    # Populate single-reference-fields (e.g. DetMediaRightsRef)
    ref_fields = emu_netx.emu_netx_refs()

    for key, value in ref_fields.items():
        if type(value) == list:
            ref_values = xml_tools.get_ref_value(emu_record, value[0], value[1])
            if ref_values is not None:
                prepped_record.find(key).text = ref_values


    # Populate grouped or ref-table fields with nested tuples (e.g. 'Creator' group, rev-attached Catalog fields)
    group_fields = emu_netx.emu_netx_groups_or_reftabs()

    for key, value in group_fields.items():
        if type(value) == list:
            if key in ['CatDepartment', 'CatCatalog'] and mm_catalog is not None:
                grouped_value = xml_tools.get_group_value(mm_catalog, value[0], value[1])

            else:
                grouped_value = xml_tools.get_group_value(emu_record, value[0], value[1])

            prepped_record.find(key).text = grouped_value


    # Populate fields where values need concatenation (e.g. reverse-attached Event fields)
    concat_fields = emu_netx.emu_netx_ref_concatenate()

    for key,value in concat_fields.items():

        # TODO - loop through for multiple reverse-attachments of one kind (e.g. if >1 rev-attached Event records)

        concat_values = None
        
        if type(value) == list:
            if type(value[1]) == list:
                if len(mm_event.findall('.//' + value[1][0])) > 0:
                    concat_values_raw = []

                    for field_name in value[1]:
                        concat_value = mm_event.find('.//' + field_name).text
                        if concat_value == None:
                            concat_value = 'NULL, check EMu'

                        concat_values_raw.append(concat_value)

                    concat_values = ' | '.join(concat_values_raw)
                    prepped_record.find(key).text = concat_values
                    # print('concat_vals = ' + str(prepped_record.find(key).text))

            elif key == 'EveEventURLs':
                if len(mm_event.findall('.//' + value[1])) > 0:
                    prepped_record.find(key).text = 'https://pj.fieldmuseum.org/event/' + mm_event.find('.//' + value[1]).text
                    # print('concat_vals = ' + str(prepped_record.find(key).text))


    return prepped_record
    

def main():  # main_xml_input, event_xml, catalog_xml):
    '''Given an input-date, prep XML export from that date'''
    
    # Setup paths to input XML
    input_date = str(sys.argv[1])
    use_live_paths = sys.argv[2]
    # output_emu_prepped = sys.argv[3]  # not useful here

    # Check if test or live paths should be used
    if use_live_paths == "LIVE":
        full_prefix = config('ORIGIN_PATH_MEDIA')
        dest_prefix = config('DESTIN_PATH_XML')
    elif use_live_paths == "TEST": 
        full_prefix = config('TEST_ORIGIN_PATH_MEDIA')
        dest_prefix = config('TEST_DESTIN_PATH_XML')
    else:
        full_prefix = config('LOCAL_ORIGIN_PATH')
        dest_prefix = config('XML_LOCAL_DESTIN_PATH')

    main_xml_input = full_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
    event_xml = full_prefix + 'NetX_mm_events/' + input_date + '/xml*'
    catalog_xml = full_prefix + 'NetX_mm_catalogue/' + input_date + '/xml*'


    # Load EMu records & fix xml-tags
    print('main_xml_input is:  ' + main_xml_input)
    emu_tree = ET.ElementTree()
    emu_records_raw1 = emu_tree.parse(glob.glob(main_xml_input)[0])  # TODO - test/try to account for empty input-dir
    emu_records_raw2 = xml_tools.fix_emu_xml_tags(emu_records_raw1)
    emu_records = xml_tools.convert_linebreaks_to_commas(emu_records_raw2)


    # Import Event & Catalog exports too
    eve_raw1 = ET.ElementTree().parse(glob.glob(event_xml)[0])
    cat_raw1 = ET.ElementTree().parse(glob.glob(catalog_xml)[0])
    
    eve_records_raw2 = xml_tools.fix_emu_xml_tags(eve_raw1)
    cat_records_raw2 = xml_tools.fix_emu_xml_tags(cat_raw1)

    # Prep DSS output as ET Element -- appendable, similar to a [list]
    dss_records = ET.Element('emultimedia')

    # # smaller test-set
    # emu_records = emu_records[:10]


    # loop through & prep EMu records
    for emu_record in emu_records:

        # grab corresponding Event & Catalog, if any:
        mm_event = None
        mm_catalog = None

        for event_record in eve_records_raw2:
            if event_record.find('AudIdentifier').text == emu_record.find('AudIdentifier').text:
                if event_record.findall('AdmGUIDValue') is not None:
                    mm_event = event_record
                    # print("event = " + str(mm_event.findall('./')))
        
        for cat_record in cat_records_raw2:
            if cat_record.find('AudIdentifier').text == emu_record.find('AudIdentifier').text:
                mm_catalog = cat_record


        # loop thru dss schema fields & populate from EMu xml
        prepped_record = parse_emu_to_dss(emu_record, mm_event, mm_catalog)

        if prepped_record is not None:
            dss_records.append(prepped_record)


    # Output Prepped DSS-XML
    if len(dss_records) > 1:
        if os.path.exists(dest_prefix) == False:
            os.makedirs(dest_prefix)
        
        with open(dest_prefix + "dss_prepped.xml", 'wb') as f:
            f.write(
                ET.tostring(
                    dss_records, 
                    xml_declaration=True,
                    encoding='utf-8',
                    short_empty_elements=True
                    )
                )
    

    # if output_emu_prepped == True:

    #     emu_out = ET.Element('emultimedia')
    #     for emu in emu_records:
    #         emu_out.append(emu)

    #     if os.path.exists(dest_prefix) == False:
    #         os.makedirs(dest_prefix)

    #     with open(dest_prefix + "emu_prepped.xml", 'wb') as f:
    #         f.write(
    #             ET.tostring(
    #                 emu_out, 
    #                 xml_declaration=True,
    #                 encoding='utf-8',
    #                 short_empty_elements=True
    #                 )
    #             )


if __name__ == '__main__':
    main()