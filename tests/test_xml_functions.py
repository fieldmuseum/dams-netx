import unittest

"""
To execute tests, run this command from the root dir:

python3 -m unittest tests/test_xml_functions.py
"""
class XMLFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        """Set up here"""

    def test_xml_file_can_be_parsed(self):
        """Verify that the EMu-exported XML file can be parsed"""
