'''
Tests for prep_emu_xml.py

python3 -m unittest tests/test_utils_xml_tools.py

'''
import glob, unittest, sys
import xml.etree.ElementTree as ET
from dotenv import dotenv_values

from utils.xml_tools import convert_linebreaks_to_commas, fix_emu_xml_tags

class XMLToolsTestCase(unittest.TestCase):
    def setUp(self) -> None:

        config = dotenv_values(".env")
        if not config: raise Exception("No .env config file found")

        netx_env = "TEST"
        
        if netx_env == "LIVE":
            print("CAUTION - Tests are running in LIVE NetX env")
            sys.exit(1)
            
        else:
            print("Tests are running in TEST NetX env")
            full_prefix = config['TEST_ORIGIN_PATH_XML']
            dest_prefix = config['TEST_DESTIN_PATH_XML']

        test_subdir = "test5"
        self.main_xml_input = full_prefix + 'NetX_emultimedia/' + test_subdir + '/xml*'

        emu_tree = ET.ElementTree()
        self.emu_records_raw = emu_tree.parse(glob.glob(self.main_xml_input)[0])  # TODO - test/try to account for empty input-dir

        # return super().setUp()


    def test_fix_emu_xml_tags(self):
        """Test if fix_emu_xml_tags returns EMu column names as tag-names"""
        
        test_xml = fix_emu_xml_tags(self.emu_records_raw)

        for child_node in test_xml:
            for emu_column in child_node:
                # print(emu_column.tag)
                self.assertNotEqual("atom", emu_column.tag)
                self.assertEqual(0, len(emu_column.attrib))


    def test_convert_linebreaks_to_commas(self):
        """Test if linebreaks are converted to commas"""

        test_xml = fix_emu_xml_tags(self.emu_records_raw)
        test_xml = convert_linebreaks_to_commas(test_xml)

        for child_node in test_xml:
            for emu_column in child_node:
                if str(emu_column.tag) == "DetSubject_tab":
                    self.assertRegex(emu_column.text, r'^"')
                    self.assertRegex(emu_column.text, r'"$') #, 'string has ending-quote')
                    # self.assertIn(r'^"', emu_column.text)
                    # self.assertIn(r'"$', emu_column.text)
                    print(emu_column.text)

                    for tuple in emu_column:
                        print(len(tuple))
                        for atom in tuple:
                            print(f'convert -- {atom.text}')
                # self.assertNotEqual("atom", emu_column.tag)
                # self.assertEqual(0, len(emu_column.attrib))        

    # def test_convert_pipe_to_unique_commas(self):
    #     """"""


    # def test_get_ref_value(self):
    #     """"""


    # def test_get_group_value(self):
    #     """"""


    # def test_get_unique_group_value(self):
    #     """"""

