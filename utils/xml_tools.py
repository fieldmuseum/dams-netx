'''
Tools for prepping/reshaping XML
'''

import re
import xml.etree.ElementTree as ET

def convert_linebreaks_to_commas(root):
    '''Convert an EMu table field to comma-delimited quoted values'''
    for table_as_text in root.findall('.//*'):
        if table_as_text.tag is not None:
            if table_as_text.tag.find("_tab") > 0:  # and table_as_text.text.find("\n") > 0:
                row_list = []
                for tuple in table_as_text:
                    for row in tuple:

                        if row.text is not None:
                            row_list.append(row.text)

                if len(row_list) > 0:
                    table_as_text.text = '","'.join(row_list)
                    table_as_text.text = '"' + table_as_text.text + '"'
                    row_list = None

    return root


def fix_emu_xml_tags(emu_records: ET.Element) -> ET.Element:
    '''Move EMu column names from nested "name" attribute to XML tag'''

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


def get_ref_value(emu_record: ET.Element, ref_tag: ET.Element, child_tag: str) -> str:
    '''
    Given an EMu xml group-label for multi-value table-fields, 
    return the value of a nested or child field to populate a netx field
    '''

    child_list = []
    nested_child_tag = None

    # len(re.findall(r'\.', str(child_tag)) > 0:
    if child_tag.find('.') > 0:
        print('got 1 - ' + child_tag)
        nested_tag = child_tag.split(".")
        print(nested_tag)
        child_tag = nested_tag[0]
        nested_child_tag = nested_tag[1]

    # else:
    for child_field in emu_record.find(ref_tag): 
        # for child_field in tuple:

        if child_field.tag == child_tag:
            # print(str(child_field.tag) + ' = ' + str(child_field.text))

            if nested_child_tag is not None:

                for tuple in child_field:
                    for nested_child_field in tuple:
                        print(nested_child_field.tag)
                        if nested_child_field.tag == nested_child_tag:
                            print('nested ' + str(child_field.tag) + ' = ' + str(child_field.text))
                            child_list.append(nested_child_field.text)

            else:
                child_list.append(str(child_field.text))
            
    if len(child_list) > 0:
        netx_attr = " | ".join(child_list)
    
    else: netx_attr = None
    
    return netx_attr


def get_grouped_value(emu_record: ET.Element, group_tag: ET.Element, child_tag: str) -> str:
    '''
    Given an EMu xml group-label for multi-value table-fields, 
    return the flattened values of a nested or child field to populate a netx field
    '''

    child_list = []
    for tuple in emu_record.find(group_tag): 
        for child_field in tuple:
            if str(child_field.tag) == child_tag:
                child_list.append(child_field.text)
            
    netx_attr = " | ".join(child_list)

    return netx_attr
