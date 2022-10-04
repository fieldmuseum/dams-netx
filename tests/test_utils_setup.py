import collections, unittest, os
from dotenv import dotenv_values

from utils.setup import get_config_dams_netx, get_path_from_env, get_sys_argv

"""
Tests for setup utils

python3 -m unittest tests/test_setup.py
"""

class NetxSetupUtilsTestCase(unittest.TestCase):

    def test_get_config(self):
        """Tests that get_config_dams_netx() properly loads & returns env variables"""

        config = get_config_dams_netx("TEST")
        print(f' env  = {config["NETX_ENV"]}')
        print(type(config))
        self.assertEqual(type(config), collections.OrderedDict)

        self.assertIn("ORIGIN_PATH_MEDIA", config)
        self.assertIn("DESTIN_PATH_MEDIA", config)
        self.assertIn("ORIGIN_PATH_XML", config)
        self.assertIn("DESTIN_PATH_XML", config)
        self.assertIn("TEST_ORIGIN_PATH_MEDIA", config)
        self.assertIn("TEST_DESTIN_PATH_MEDIA", config)
        self.assertIn("TEST_ORIGIN_PATH_XML", config)
        self.assertIn("TEST_DESTIN_PATH_XML", config)
        self.assertIn("NETX_ENV", config)

        self.assertTrue(os.path.exists(config['ORIGIN_PATH_MEDIA']))
        self.assertTrue(os.path.exists(config['DESTIN_PATH_MEDIA']))
        self.assertTrue(os.path.exists(config['ORIGIN_PATH_XML']))
        self.assertTrue(os.path.exists(config['DESTIN_PATH_XML']))
        self.assertTrue(os.path.exists(config['TEST_ORIGIN_PATH_MEDIA']))
        self.assertTrue(os.path.exists(config['TEST_DESTIN_PATH_MEDIA']))
        self.assertTrue(os.path.exists(config['TEST_ORIGIN_PATH_XML']))
        self.assertTrue(os.path.exists(config['TEST_DESTIN_PATH_XML']))
        

    # def test_get_sys_argv(self):
    #     """Tests that get_config_dams_netx() properly loads & returns env variables"""

    #     test_or_live = get_sys_argv(1)
    #     print(test_or_live)
    #     self.assertEqual(type(test_or_live), str)


    def test_get_path_from_env(self):
        """Tests that get_config_dams_netx() properly loads & returns env variables"""

        path_from_env_live = get_path_from_env("LIVE", "path/to/live", "path/to/test")
        self.assertEqual(path_from_env_live, "path/to/live")


        config = get_config_dams_netx("TEST")

        path_from_env = get_path_from_env(config['NETX_ENV'], "path/to/live", "path/to/test")
        self.assertEqual(path_from_env, "path/to/test")


    # def test_netx_start_log(self):
    #     """Tests that netx_get_folder_by_path returns folder info"""
        

    # def test_netx_stop_log(self):
    #     """Tests that netx_get_folder_by_path returns folder info"""
        