import unittest, csv, random
import utils.netx_api as netx_api

"""
Tests for netx_api utils

python3 -m unittest tests/test_netx_api.py
"""
class NetxAPIUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.csvrows = []
        with open('data/csv_good_examples/pathAdd_20220811_test.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader: self.csvrows.append(row)

    def test_netx_get_asset_by_filename(self):
        """Tests that netx_get_asset_by_filename returns asset info"""

        random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        filename = random_row[0]
        netx_asset = netx_api.netx_get_asset_by_filename(filename)
        self.assertNotIn("error", netx_asset)
        
        # TODO: once the query works properly, assert we're getting back some of the correct
        # data. e.g. Check for dict keys, using assertIn, etc.

    def test_netx_get_folder_by_path(self):
        """Tests that netx_get_folder_by_path returns folder info"""
        
        random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        folder = random_row[1]
        netx_folder = netx_api.netx_get_folder_by_path(folder)
        self.assertNotIn("error", netx_folder)
        
        # TODO: once the query works properly, assert we're getting back some of the correct
        # data. e.g. Check for dict keys, using assertIn, etc.

    def test_netx_add_asset_to_folder(self):
        """Tests that netx_add_asset_to_folder can add asset to a folder"""

        random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        filename = random_row[0]
        folder = random_row[1]

        netx_asset = netx_api.netx_get_asset_by_filename(filename)
        netx_folder = netx_api.netx_get_folder_by_path(folder)
        self.assertNotIn("error", netx_asset)
        self.assertNotIn("error", netx_folder)

        # TODO: set up asset_id, folder_id, and additional info to test this properly
        netx_asset_transfer_info = netx_api.netx_add_asset_to_folder(asset_id, folder_id)
        self.assertNotIn("error", netx_asset_transfer_info)
