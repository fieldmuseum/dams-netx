# Parse EMu XML to DAMS-ready XML
# 2022-Jun; FMNH, based on EMu-xml-to-json convert_xml.py

from lxml import etree
from glob import glob
from decouple import config
from bs4 import BeautifulSoup
import sys
import xml.etree.ElementTree as ET
import prep_xml_input as pi


def xml_to_json(xml_input, emu_xml_out=True):

    # # # # # # # # # # # #
    # Prep input-XML  # # # 
    
    # Turn EMu col-names into XML-tags:
    tree1_string = pi.xml_prep(xml_in = xml_input)
    tree_prep = etree.XML(tree1_string)

    # # Remove redacted values
    # tree_prep = ri.redact_input(tree_prep, map_condition, emu_map)

    # Return updated xml as string to switch to lxml.etree
    prep_tree_string = etree.tostring(tree_prep).decode('utf-8')

    # Convert back to xml ElementTree
    doc = ET.fromstring(prep_tree_string)
    tree = ET.ElementTree(doc)

    # Fixed EMu-XML
    if emu_xml_out == True:
        # Output compact xml -- e.g. <tag />
        tree.write(config('XML_OUT_PATH') + "emu_prepped.xml", encoding='utf-8')    

        # Output 'canonic' xml -- e.g. <tag></tag>
        # # Commented out until can fix with Ubuntu
        with open(config('XML_OUT_PATH') + "emu_raw_canonic.xml", mode='w', encoding='utf-8') as out_file:
            ET.canonicalize(xml_data=tree1_string, out=out_file)


# To run convert_xml.py directly, run:
#   python3 convert_xml.py file1 file2 etc
if __name__ == '__main__':
    for arg in sys.argv[1:]:
        for filename in glob(arg):
            xml_to_json(arg, emu_xml_out=True)