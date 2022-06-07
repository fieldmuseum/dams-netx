'''
Parse EMu XML to DAMS-ready XML
2022-Jun; FMNH, based on EMu-xml-to-json convert_xml.py
'''


# from xml.etree.ElementTree import tostring
import xml.etree.ElementTree as ET
import re, sys  # lxml.etree, lxml.html, 
# from bs4 import BeautifulSoup  # use them all bc xml+python=pita
# from lxml import etree, html
# from dict2xml import dict2xml
from glob import glob
from decouple import config
import utils.dss_schema as dss_schema


# import xml.etree.ElementTree as ET  # avoid confusion w/ lxml
# import prep_xml_input as pi

def parse_emu_to_dss(emu_record: ET.Element, dss_schema_xml: ET.Element) -> ET.Element:
    '''Parse exported EMu records to DSS-schema records'''

    # Setup record's DSS fields
    prepped_record = dss_schema_xml

    # print(ET.tostring(prepped_record))


    # TODO - Abstract to populate atomic vs table/etc fields:

    # Populate DSS fields
    # if len(emu_record.findall('.//tuple/atom[@name="irn"]')) > 0:
    if len(emu_record.findall('irn')) > 0:
        print(emu_record.find('irn').text)
        # prepped_record.irn = emu_record.xpath('atom[@name="irn"]')[0].text
        prepped_record.find('irn').text = emu_record.find('irn').text

    
    # if len(emu_record.xpath('atom[@name="irn"]')) > 0:
    #     prepped_record['irn'] = emu_record.xpath('atom[@name="irn"]')[0].text



    # # Replace top-level "tuple" with "data" 
    # for thing in root1:

    #     if thing.get('name') is None:
    #         if thing.tag == "tuple":
    #             thing.tag = "data"
    #         thing.set('name', thing.tag)


    # # Turn EMu col-names into XML-tags instead of attributes:
    # for child in root1.findall('.//*'):

    #     if child.tag == "tuple" and child.get('name') is None:
    #         child.set('name', 'tuple')
    #     child.tag = child.get('name')
    #     child.attrib = {}

    return prepped_record





def convert_linebreaks_to_commas(root):
    '''convert an EMu table-as-text field to comma-delimited'''
    for table_as_text in root.findall('.//*'):
        if table_as_text.get('name') is not None:
            if table_as_text.get('name').find("_tab") > 0 and table_as_text.text.find("\n") > 0:
                table_as_text.text = re.sub('\n', '","', table_as_text.text)
                table_as_text.text = '"' + table_as_text.text + '"'

    return root

def emu_xml_fix(emu_records):
    # Replace top-level "tuple" with "data" 
    for thing in emu_records:

        if thing.get('name') is None:
            if thing.tag == "tuple":
                thing.tag = "data"
            thing.set('name', thing.tag)


    # Turn EMu col-names into XML-tags instead of attributes:
    for child in emu_records.findall('.//*'):

        if child.tag == "tuple" and child.get('name') is None:
            child.set('name', 'tuple')
        child.tag = child.get('name')
        child.attrib = {}
    
    return emu_records
    

def xml_to_json(xml_input):

    # # # # # # # # # # # #
    # Prep input-XML  # # # 
    
    # # Turn EMu col-names into XML-tags:

    # tree = lxml.html.parse(xml_input)  # 'tests/data_in/2022-6-3/xml64963-151829.000000'
    # tree_records = tree.xpath('.//table[@name="emultimedia"]/tuple')

    emu_tree = ET.ElementTree()
    emu_records_raw = emu_tree.parse(xml_input)
    emu_records = emu_xml_fix(emu_records_raw)
    

    # load dss schema
    dss_mm_schema = dss_schema.media_schema_xml()

    # Parse/Prep records
    # dss_records = []
    # dss_tree = ET.ElementTree()
    dss_records = ET.Element('emultimedia')  # dss_tree.getroot()


    for emu_record in emu_records:
        # loop thru dss schema fields & populate from EMu xml
        prepped_record = parse_emu_to_dss(emu_record, dss_mm_schema)

        # print(prepped_record)

        if prepped_record is not None:
            dss_records.append(prepped_record)



    # # Fixed EMu-XML
    # if emu_xml_out == True:
    #     # Output compact xml -- e.g. <tag />
    if len(dss_records) > 1:

        # dss_tree = ET.ElementTree(dss_records)
        # dss_tree.write(
        #     config('XML_OUT_PATH') + "emu_prepped.xml", 
        #     xml_declaration = True,
        #     encoding='utf-8',
        #     short_empty_elements=True
        #     )   
        
        with open(config('XML_OUT_PATH') + "emu_preppedALT.xml", 'wb') as test_file:
            test_file.write(
                ET.tostring(
                    dss_records, 
                    xml_declaration=True,
                    encoding='utf-8',
                    short_empty_elements=True
                    )
                )  # , xml_declaration = True, encoding='utf-8')
 

    #     # # Output 'canonic' xml -- e.g. <tag></tag>
    #     # # # Commented out until can fix with Ubuntu
    #     # with open(config('XML_OUT_PATH') + "emu_raw_canonic.xml", mode='w', encoding='utf-8') as out_file:
    #     #     ET.canonicalize(xml_data=tree1_string, out=out_file)

    # Output prepped records to XML for DSS
    # if len(dss_records) > 0:
    #     print("outputing")
    #     # # print(dss_records)
    #     # dss_xml_from_list = lxml.etree.Element('records')
    #     # for dss_record in dss_records:
    #     #     dss_rec_xml = dict2xml(dss_record)
    #     #     dss_xml_from_list.append(dss_rec_xml)
    #     # dss_xml_from_list.write('test_out_wtf.xml', pretty_print=True)
        
    #     dss_dict = dict2xml(dss_records)

    #     # tree = ET.ElementTree()
    #     tree = ET.fromstring(dss_dict)
    #     ET.ElementTree.write('testagain.xml')


    # with open('test_dss_string.xml', 'w') as test_file:
    #     test_file.write(dss_dict)
    # # print(dss_dict[-100:])
    # dss_soup = BeautifulSoup(dss_dict, 'lxml')
    # # dss_xml = lxml.etree.ElementTree(lxml.etree.Element(dss_dict))
    # # print(dss_xml)
    # # dss_xml.write('test_out_2.xml', pretty_print=True)
    # with open('test_output_2.xml', 'w') as f:
    #     # lxml.etree.tostring(lxml.etree.Element(dss_dict))
    #     # f.writelines(lxml.etree.tostring(lxml.etree.Element(dss_dict)))  # lxml.etree.ElementTree(dss_xml))
    #     f.write(dss_soup.prettify(formatter='xml'))


# To run convert_xml.py directly, run:
#   python3 convert_xml.py file1 file2 etc
if __name__ == '__main__':
    for arg in sys.argv[1:]:
        for filename in glob(arg):
            xml_to_json(arg)