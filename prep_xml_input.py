# Prep input-XML
# 2022-Jun; FMNH, based on EMu-xml-to-json prep_input.py


import xml.etree.ElementTree as ET
from glob import glob
import re, sys


def xml_prep(xml_in, linebreaks_to_commas=True):


    # # # # # # # # # # #
    # Prep input-xml  # # 
    tree1 = ET.parse(xml_in)
    root1 = tree1.getroot()


    # Replace "table" "tag with table-name
    root1.tag = root1.get('name')
    root1.attrib = {}


    # Convert linebreaks fields to commas ('linebreaks_to_commas' option)
    # ...For table-as-text fields:
    if linebreaks_to_commas == True:
        for table_as_text in root1.findall('.//*'):
            if table_as_text.get('name') is not None:
                if table_as_text.get('name').find("_tab") > 0 and table_as_text.text.find("\n") > 0:
                    table_as_text.text = re.sub('\n', '","', table_as_text.text)
                    table_as_text.text = '"' + table_as_text.text + '"'


    # Replace top-level "tuple" with "data" 
    for thing in root1:

        if thing.get('name') is None:
            if thing.tag == "tuple":
                thing.tag = "data"
            thing.set('name', thing.tag)


    # Turn EMu col-names into XML-tags instead of attributes:
    for child in root1.findall('.//*'):

        if child.tag == "tuple" and child.get('name') is None:
            child.set('name', 'tuple')
        child.tag = child.get('name')
        child.attrib = {}


    tree1_string = ET.tostring(tree1.getroot())

    return tree1_string


# To run convert_xml.py directly, run:
#   python3 convert_xml.py file1 file2 etc
if __name__ == '__main__':
    for arg in sys.argv[1:]:
        for filename in glob(arg):
            xml_prep(arg)
            