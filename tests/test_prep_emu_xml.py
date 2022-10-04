'''
Tests for prep_emu_xml.py

python3 -m unittest tests/test_prep_emu_xml.py

'''
import glob, unittest, sys
import xml.etree.ElementTree as ET
from dotenv import dotenv_values

class PrepEMuXmlTestCase(unittest.TestCase):
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

        # return super().setUp()

    def test_xml_file_can_be_parsed(self):
        """Verify that the EMu-exported XML file is well formed / can be parsed"""
        # Load EMu records & fix xml-tags
        emu_tree = ET.ElementTree()
        emu_records_raw = emu_tree.parse(glob.glob(self.main_xml_input)[0])  # TODO - test/try to account for empty input-dir
        self.assertEqual(type(emu_records_raw),ET.Element)



# TODO 1
# check that mm attached to multiple ecatalogue records have their Cat/Dept values parsed properly
# test with guid 66f7f84d-9ba3-48ad-afaf-7f254bf289d6

# TODO 2
#   File "/home/scripts/dams-netx/prep_emu_media.py", line 215, in get_folder_hierarchy
#    return dept_level_1[dept_emu.index(department)] + '/'
# test with real vs not-real secDept values
# For not-real, should move record to exceptions dir like lost/found + handle/log this error:  ValueError: 'Legal' is not in list
