'''
Parse EMu XML to DAMS-ready XML
2022-Jun; FMNH, based on EMu-xml-to-json convert_xml.py
'''

import xml.etree.ElementTree as ET
import re, sys
from glob import glob
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

    for key,value in concat_fields:
        if type(value) == list:
            if type(value[1]) == list:
                ' | '.join(value[1])
            elif key == 'EveEventURLs' and mm_event is not None:
                prepped_record.find(key).text = 'https://pj.fieldmuseum.org/event/' + mm_event.find(value[1]).text
            concat_values = xml_tools.get_group_value(emu_record, value[0], value[1])
            prepped_record.find(key).text = concat_values



    return prepped_record
    

def main(main_xml_input, event_xml, catalog_xml, output_emu_prepped=True):
    '''Prep input-XML'''
    
    # Load EMu records & fix xml-tags
    emu_tree = ET.ElementTree()
    emu_records_raw1 = emu_tree.parse(main_xml_input)
    emu_records_raw2 = xml_tools.fix_emu_xml_tags(emu_records_raw1)
    emu_records = xml_tools.convert_linebreaks_to_commas(emu_records_raw2)

    # Import Event & Catalog exports too
    eve_raw1 = emu_tree.parse(event_xml)
    cat_raw1 = emu_tree.parse(catalog_xml)
    
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
                mm_event = event_record
        
        for cat_record in cat_records_raw2:
            if cat_record.find('AudIdentifier').text == emu_record.find('AudIdentifier').text:
                mm_catalog = cat_record


        # loop thru dss schema fields & populate from EMu xml
        prepped_record = parse_emu_to_dss(emu_record, mm_event, mm_catalog)

        if prepped_record is not None:
            dss_records.append(prepped_record)


    # Output Prepped DSS-XML
    if len(dss_records) > 1:
        
        with open(config('XML_OUT_PATH') + "dss_prepped.xml", 'wb') as f:
            f.write(
                ET.tostring(
                    dss_records, 
                    xml_declaration=True,
                    encoding='utf-8',
                    short_empty_elements=True
                    )
                )
    
    emu_out = ET.Element('emultimedia')
    for emu in emu_records:
        emu_out.append(emu)
    

    if output_emu_prepped == True:
        with open("data/emu_prepped.xml", 'wb') as f:
            f.write(
                ET.tostring(
                    emu_out, 
                    xml_declaration=True,
                    encoding='utf-8',
                    short_empty_elements=True
                    )
                )

# To run convert_xml.py directly, run:
#   python3 convert_xml.py file1 file2 etc
if __name__ == '__main__':
    for arg in sys.argv[1:]:
        for filename in glob(arg):
            main(arg)