'''
Tools for prepping/reshaping XML
'''

import re

def convert_linebreaks_to_commas(root):
    '''convert an EMu table-as-text field to comma-delimited'''
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


def emu_xml_tag_fix(emu_records):
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