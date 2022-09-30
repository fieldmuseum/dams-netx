"""
Tests for netx_api utils

python3 -m unittest tests/test_netx_api.py
"""

import unittest, csv, random, sys
import utils.netx_api as netx_api
from dotenv import dotenv_values

class NetxAPIUtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.csvrows = []
        with open('data/csv_good_examples/pathAdd_20220811_test.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader: self.csvrows.append(row)

        random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        self.asset_name = random_row[0]
        self.folder_name = random_row[1]
        
        # QUESTIONS on added setup:

        # Q1 - Are any env-variables/overrides or safety-nets needed or does this clutter?
        config = dotenv_values(".env")
        if not config: raise Exception("No .env config file found")
        
        # Q2 - Is there a way (or bad idea) to hard-code NetX env to "TEST"?
        # netx_env = config['NETX_ENV']
        netx_env = "TEST"
        
        # For now, static values for each env:
        if netx_env == "LIVE":
            print("CAUTION - Tests are running in LIVE NetX env")
            sys.exit(1)
            # self.asset_id = 0  # this will error
            # self.folder_id = 0  # this will error

        else:
            print("Tests are running in ")
            self.static_asset_id = 18201  # "featherswitheye.png" test-image
            self.static_folder_id = 341  #  "NetX Test" test-folder
        
        # TODO: 
        # -- check config for up-to-date API token 
        #    - e.g. if request status_code == 415: ... (not sure that's specific to token-issue tho)


    def test_netx_get_asset_by_filename(self):
        """Tests that netx_get_asset_by_filename returns asset info"""

        # random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        # filename = random_row[0]
        netx_asset = netx_api.netx_get_asset_by_filename(self.asset_name, netx_env="TEST")
        print(' asset  = ' + str(netx_asset))
        self.assertNotIn("error", netx_asset)
        self.assertIn("result", netx_asset)

        # assert that the correct data/dict keys return
        self.assertIn("results", netx_asset['result'])
        self.assertEqual(type(netx_asset['result']['results']), list)
        self.assertIn('id', netx_asset['result']['results'][0].keys())
        

    def test_netx_get_folder_by_path(self):
        """Tests that netx_get_folder_by_path returns folder info"""
        
        # random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        # folder = random_row[1]
        netx_folder = netx_api.netx_get_folder_by_path(self.folder_name, netx_env="TEST")
        print(' folder = ' + str(netx_folder))
        self.assertNotIn("error", netx_folder)
        self.assertIn("result", netx_folder)

        # assert that the correct data/dict keys return
        self.assertIn("id", netx_folder['result'])


    def test_netx_add_asset_to_folder(self):
        """Tests that netx_add_asset_to_folder can add asset to a folder"""

        netx_asset = netx_api.netx_get_asset_by_filename(self.asset_name, ['asset.id','asset.folders'], netx_env="TEST")
        self.assertNotIn("error", netx_asset)
        self.assertIn("result", netx_asset)

        asset_id = netx_asset['result']['results'][0]['id']

        # check/make sure that asset is NOT in folder before adding
        netx_asset_prep = netx_api.netx_remove_asset_from_folder(asset_id, self.static_folder_id, netx_env="TEST")
        print(' netx_asset_prep = ' + str(netx_asset_prep))
        if "error" not in netx_asset_prep:
            asset_pretest_folders = [folder['id'] for folder in netx_asset_prep['result']['folders']]
            self.assertNotIn(self.static_folder_id, asset_pretest_folders)
        else:
            self.assertIn(('code',1000), netx_asset_prep['error'].items())
        

        # test that asset was added without errors
        netx_asset_transfer_info = netx_api.netx_add_asset_to_folder(asset_id, self.static_folder_id, netx_env="TEST")
        self.assertNotIn("error", netx_asset_transfer_info)
        asset_posttest_folders = [folder['id'] for folder in netx_asset_transfer_info['result']['folders']]
        self.assertIn(self.static_folder_id, asset_posttest_folders)

        # clean up/reset asset post-test
        netx_asset_transfer_info = netx_api.netx_remove_asset_from_folder(asset_id, self.static_folder_id, netx_env="TEST")


    def test_netx_remove_asset_from_folder(self):
        """Tests that netx_remove_asset_from_folder can remove asset from a folder"""

        netx_asset = netx_api.netx_get_asset_by_filename(self.asset_name, ['asset.id','asset.folders'], netx_env="TEST")
        self.assertNotIn("error", netx_asset)
        self.assertIn("result", netx_asset)

        asset_id = netx_asset['result']['results'][0]['id']

        # check that asset IS in folder before removing
        netx_asset_folder_setup = netx_api.netx_add_asset_to_folder(asset_id, self.static_folder_id, netx_env="TEST")
        asset_pretest_folders = [folder['id'] for folder in netx_asset_folder_setup['result']['folders']]
        self.assertIn(self.static_folder_id, asset_pretest_folders)
        self.assertNotIn("error", asset_pretest_folders)

        # Test removing asset from folder
        netx_asset_transfer_info = netx_api.netx_remove_asset_from_folder(asset_id, self.static_folder_id, netx_env="TEST")
        self.assertNotIn("error", netx_asset_transfer_info)
        asset_posttest_folders = [folder['id'] for folder in netx_asset_transfer_info['result']['folders']]
        self.assertNotIn(self.static_folder_id, asset_posttest_folders)
