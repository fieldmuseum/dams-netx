'''
Tools for prepping/reshaping XML
'''

import re
import xml.etree.ElementTree as ET


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


def convert_linebreaks_to_commas(emu_records: ET.Element) -> ET.Element:
    '''Convert an EMu table field to comma-delimited quoted values'''
    for table_as_text in emu_records.findall('.//*'):
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

    return emu_records


def convert_pipe_to_unique_commas(pipe_delim_string:str) -> str:
    '''Convert a pipe-delimited string to comma-delimited quoted values'''

    # if re.match(r'\s*\|\s*', pipe_delim_string) is None:
    #     raise Exception("Pipes not found in input string")

    comma_text = None
    comma_list = []

    if pipe_delim_string is None:
        raise Exception("No input string found")
        
    pipe_list = pipe_delim_string.split(" | ")

    for list_item in pipe_list:
        if list_item is not None and list_item not in comma_list:
            comma_list.append(list_item)

    if len(comma_list) > 0:
        comma_text = '","'.join(comma_list)
        comma_text = '"' + comma_text + '"'

    return comma_text


def get_ref_value(emu_record: ET.Element, ref_tag: ET.Element, child_tag: str) -> str:
    '''
    Given an EMu xml group-label for multi-value table-fields, 
    return the value of a nested or child field to populate a netx text-field
    '''

    child_list = []
    nested_child_tag = None
    nested_tag = None
    netx_attr = None

    if child_tag.find('.') > 0:
        nested_tag = child_tag.split(".")
        child_tag = nested_tag[0]
        nested_child_tag = nested_tag[1]

    for child_field in emu_record.find(ref_tag): 
        if child_field.tag == child_tag:
            if nested_child_tag is not None:
                for tuple in child_field:
                    for nested_child_field in tuple:
                        if nested_child_field.tag == nested_child_tag:
                            if nested_child_field.text is not None:  # and re.match(r'^\s+$', nested_child_field.text) is None:
                                child_list.append(nested_child_field.text)

            elif child_field.text is not None:
                child_list.append(str(child_field.text))

    if len(child_list) > 0: 
        netx_attr = " | ".join(child_list)

    return netx_attr


def get_group_value(emu_record: ET.Element, group_tag: ET.Element, child_tag: str) -> str:
    '''
    Given an EMu xml group-label for multi-value table-fields, 
    return the flattened values of a nested or child field to populate a netx text-field
    '''

    child_list = []

    if emu_record.find(group_tag) is not None:
        for tuple in emu_record.find(group_tag): 
            for child_field in tuple:
                if str(child_field.tag) == child_tag:
                    child_list.append(str(child_field.text))

    if len(child_list) > 0:
        netx_attr = " | ".join(child_list)

    else: netx_attr = None
    
    return netx_attr


def get_unique_group_value(emu_record: ET.Element, group_tag: ET.Element, child_tag: str) -> str:
    '''
    Given an EMu xml group-label for multi-value table-fields, 
    return the unique values of a nested or child field to populate a netx tag-field
    '''

    netx_attr = None
    child_list = []

    if emu_record.find(group_tag) is not None:
        for tuple in emu_record.find(group_tag): 
            for child_field in tuple:
                if str(child_field.tag) == child_tag:
                    if str(child_field.text) not in child_list:
                        child_list.append(str(child_field.text))

    if len(child_list) > 0:
        netx_attr_raw = " | ".join(child_list)

        netx_attr = convert_pipe_to_unique_commas(netx_attr_raw)
    
    return netx_attr
