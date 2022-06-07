'''
Parse EMu XML to DAMS-ready XML
2022-Jun; FMNH, based on EMu-xml-to-json convert_xml.py
'''

import xml.etree.ElementTree as ET
import sys
from glob import glob
from decouple import config
import utils.dss_schema as dss_schema
import utils.xml_tools as xml_tools
import utils.emu_netx_map as emu_netx


def parse_emu_to_dss(emu_record: ET.Element) -> ET.Element:
    '''Parse exported EMu records to DSS-schema records'''

    # Setup record's DSS fields
    prepped_record = dss_schema.media_schema_xml()

    # Populate DSS fields for atomic EMu fields:
    atomic_fields = emu_netx.emu_netx_atoms()

    for key, value in atomic_fields.items():
        if value is not None and emu_record.find(value) is not None:
            prepped_record.find(key).text = emu_record.find(value).text


    # Populate table-fields

    table_fields = emu_netx.emu_netx_tables()

    for key, value in table_fields.items():
        if type(value) == list:
            print('figure this out')
        elif value is not None and emu_record.find(value) is not None:
            prepped_record.find(key).text = emu_record.find(value).text
    
    # prepped_record.find('DetSubject_tab').text = emu_record.find('DetSubject_tab').text

    return prepped_record
    

def main(xml_input, output_emu_prepped=True):
    '''Prep input-XML'''
    
    # Load EMu records & fix xml-tags
    emu_tree = ET.ElementTree()
    emu_records_raw1 = emu_tree.parse(xml_input)
    emu_records_raw2 = xml_tools.emu_xml_tag_fix(emu_records_raw1)
    emu_records = xml_tools.convert_linebreaks_to_commas(emu_records_raw2)

    # Prep DSS output as ET Element -- appendable, similar to a [list]
    dss_records = ET.Element('emultimedia')

    # smaller test-set
    emu_records = emu_records[:10]


    # loop through & prep EMu records
    for emu_record in emu_records:
        # loop thru dss schema fields & populate from EMu xml
        prepped_record = parse_emu_to_dss(emu_record)

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
        with open(config('XML_OUT_PATH') + "emu_prepped.xml", 'wb') as f:
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