'''
Functions for using texcdp (the EMu API)
- Based on netx_api.py functions
- texcdp docs - https://nexus.melbourne.axiell.com/texcdp/latest
'''

import datetime, re, requests
import utils.setup as setup


def emu_api_get_token(config:dict=None, user_id:str=None, user_pw:str=None) -> dict:
    '''Retrieves a JWT token from texcdp'''

    # Load the config
    if config is None:  
        config = setup.get_config_dams_netx()
        
        if not config:  raise Exception("No .env config file found")

    if user_id is None: 
        user_id = config["EMU_API_ID"]
    else:  user_id = user_id
    
    if user_pw is None: 
        user_pw = config["EMU_API_PW"]
    else:  user_pw = user_pw

    json = {
        "username":user_id,
        "password":user_pw
    }

    headers = emu_api_setup_headers()

    base_uri = config["EMU_API_BASE_URL"] + "tokens"
    
    r = requests.post(url=base_uri, headers=headers, json=json)

    return r.json()


def emu_api_setup_headers(headers:dict=None, emu_api_token:dict=None) -> dict:
    '''Sets up the required default headers for using the NetX API. Allows for overriding the headers'''

    if headers is not None: return headers

    # Set up default headers
    headers = {
        # 'Authorization': 'apiToken ' + emu_api_token,
        'Content-Type': 'application/json',
        'Prefer': 'representation=minimal'
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        # 'jsonrpc': '2.0', # 'X-Api-Version': '3',
        # 'id': '1234567890'
    }

    if emu_api_token is not None:
        headers['Authorization'] = 'Bearer' + str(emu_api_token['id'])

    return headers


def emu_api_setup_request_body(method:str, params:list) -> dict:
    '''Sets up the required request object format for the NetX API.'''

    # Check that we have json record data
    if not method: raise Exception("No NetX API method has been provided")

    # Check that we have json record data
    if not params: raise Exception("No NetX API parameter data has been provided")

    # Setup request-object
    request_object = {
        'jsonrpc': '2.0', # 'X-Api-Version': '3',
        'id': '1234',
        'method': method,  # e.g. "getAssets"
        'params': params   # list of [record-ids] and {'data' : ['fields']}
        }
    
    return request_object


def emu_api_setup_request(config:dict=None, headers:dict=None, emu_env:str=None) -> dict:
    '''Performs initial checks on a request. Returns the config, base url, and headers.'''

    # Load the config
    # config = dotenv_values(".env")
    if config is None:  
        config = setup.get_config_dams_netx()
        
        if not config:  
            raise Exception("No .env config file found")

    # Get API base URL + token for selected NetX env
    # netx_env = config["NETX_ENV"]
    if emu_env is None:
        emu_env == "TEST"

    if emu_env=="LIVE":
        emu_base_url = config["NETX_API_BASE_URL"]
        emu_api_token = config["NETX_API_TOKEN"]
    else:
        emu_base_url = config["TEST_NETX_API_BASE_URL"]
        emu_api_token = config["TEST_NETX_API_TOKEN"]


    # Set default HTTP headers
    headers = emu_api_setup_headers(headers=headers, emu_api_token=emu_api_token)

    return {'config': config, 'base_url':emu_base_url, 'headers': headers}

