"""
Tests for emu_api utils

python3 -m unittest tests/test_utils_emu_api.py
"""

import unittest, csv, random, sys
import utils.emu_api as emu_api
from dotenv import dotenv_values

class EMuAPIUtilsTestCase(unittest.TestCase):
    def setUp(self):

        config = dotenv_values(".env")
        if not config: raise Exception("No .env config file found")

        emu_env = "TEST"
        
        if emu_env == "LIVE":
            print("CAUTION - Tests are running in LIVE NetX env")
            sys.exit(1)
            # self.asset_id = 0  # this will error
            # self.folder_id = 0  # this will error

        else:
            print("Tests are running in TEST NetX env")
            self.static_asset_id = 18201  # "featherswitheye.png" test-image
            self.static_folder_id = 341  #  "NetX Test" test-folder

        input_csv = 'data/csv_good_examples/pathAdd_20220811_test.csv'
        self.csvrows = []
        with open(input_csv, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            for row in reader: self.csvrows.append(row)

        random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        self.asset_name = random_row[0]
        self.folder_name = random_row[1]
        
        # TODO: 
        # -- check config for up-to-date API token 
        #    - e.g. if request status_code == 415: ... (not sure that's specific to token-issue tho)


    def test_emu_get_media_by_irn(self):
        """Tests that emu_get_asset_by_filename returns asset info"""

        # random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
        # filename = random_row[0]
        emu_asset = emu_api.emu_api_get_media(self.asset_name, emu_env="TEST")
        print(' asset  = ' + str(emu_asset))
        self.assertNotIn("error", emu_asset)
        # self.assertIn("matches", emu_asset)

        # assert that the correct data/dict keys return
        self.assertIn("results", emu_asset['result'])
        self.assertEqual(type(emu_asset['result']['results']), list)
        self.assertIn('id', emu_asset['result']['results'][0].keys())
        

    # def test_emu_get_folder_by_path(self):
    #     """Tests that emu_get_folder_by_path returns folder info"""
        
    #     # random_row = random.choice(self.csvrows) # Get a random filename for unexpectedness
    #     # folder = random_row[1]
    #     emu_folder = emu_api.emu_get_folder_by_path(self.folder_name, emu_env="TEST")
    #     print(' folder = ' + str(emu_folder))
    #     self.assertNotIn("error", emu_folder)
    #     self.assertIn("result", emu_folder)

    #     # assert that the correct data/dict keys return
    #     self.assertIn("id", emu_folder['result'])


    # def test_emu_add_asset_to_folder(self):
    #     """Tests that emu_add_asset_to_folder can add asset to a folder"""

    #     emu_asset = emu_api.emu_get_asset_by_filename(self.asset_name, ['asset.id','asset.folders'], emu_env="TEST")
    #     self.assertNotIn("error", emu_asset)
    #     self.assertIn("result", emu_asset)

    #     asset_id = emu_asset['result']['results'][0]['id']

    #     # check/make sure that asset is NOT in folder before adding
    #     emu_asset_prep = emu_api.emu_remove_asset_from_folder(asset_id, self.static_folder_id, emu_env="TEST")
    #     print(' emu_asset_prep = ' + str(emu_asset_prep))
    #     if "error" not in emu_asset_prep:
    #         asset_pretest_folders = [folder['id'] for folder in emu_asset_prep['result']['folders']]
    #         self.assertNotIn(self.static_folder_id, asset_pretest_folders)
    #     else:
    #         self.assertIn(('code',1000), emu_asset_prep['error'].items())
        

    #     # test that asset was added without errors
    #     emu_asset_transfer_info = emu_api.emu_add_asset_to_folder(asset_id, self.static_folder_id, emu_env="TEST")
    #     self.assertNotIn("error", emu_asset_transfer_info)
    #     asset_posttest_folders = [folder['id'] for folder in emu_asset_transfer_info['result']['folders']]
    #     self.assertIn(self.static_folder_id, asset_posttest_folders)

    #     # clean up/reset asset post-test
    #     emu_asset_transfer_info = emu_api.emu_remove_asset_from_folder(asset_id, self.static_folder_id, emu_env="TEST")


    # def test_emu_remove_asset_from_folder(self):
    #     """Tests that emu_remove_asset_from_folder can remove asset from a folder"""

    #     emu_asset = emu_api.emu_get_asset_by_filename(self.asset_name, ['asset.id','asset.folders'], emu_env="TEST")
    #     self.assertNotIn("error", emu_asset)
    #     self.assertIn("result", emu_asset)

    #     asset_id = emu_asset['result']['results'][0]['id']

    #     # check that asset IS in folder before removing
    #     emu_asset_folder_setup = emu_api.emu_add_asset_to_folder(asset_id, self.static_folder_id, emu_env="TEST")
    #     asset_pretest_folders = [folder['id'] for folder in emu_asset_folder_setup['result']['folders']]
    #     self.assertIn(self.static_folder_id, asset_pretest_folders)
    #     self.assertNotIn("error", asset_pretest_folders)

    #     # Test removing asset from folder
    #     emu_asset_transfer_info = emu_api.emu_remove_asset_from_folder(asset_id, self.static_folder_id, emu_env="TEST")
    #     self.assertNotIn("error", emu_asset_transfer_info)
    #     asset_posttest_folders = [folder['id'] for folder in emu_asset_transfer_info['result']['folders']]
    #     self.assertNotIn(self.static_folder_id, asset_posttest_folders)
