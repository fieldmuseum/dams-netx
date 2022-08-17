'''
Functions for using the NetX JSON-RPC API
- Based on dato_http_api.py functions
- NetX API docs - https://developer.netx.net
'''

import requests
from dotenv import dotenv_values


def netx_api_setup_headers(headers=None, netx_api_token=None) -> dict:
    '''Sets up the required default headers for using the NetX API. Allows for overriding the headers'''

    if headers is not None: return headers

    # Set up default headers
    headers = {
        'Authorization': 'apiToken ' + netx_api_token,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        # 'jsonrpc': '2.0', # 'X-Api-Version': '3',
        # 'id': '1234567890'
    }

    return headers


def netx_api_setup_json(method:str=None, params:list=None) -> dict:
    '''Sets up the required request object format for the NetX API. '''

    # Check that we have json record data
    if not method: raise Exception("No NetX API method has been provided")

    # Check that we have json record data
    if not params: raise Exception("No NetX API parameter data has been provided")

    # Setup request-object
    request_object = {
        'jsonrpc': '2.0', # 'X-Api-Version': '3',
        'id': '12345',
        'method': method,  # e.g. "getAssets"
        'params': params   # list of [record-ids] and {'data' : ['fields']}
        }
    
    return request_object


def netx_api_setup_request(headers=None) -> dict:
    '''Performs initial checks on a request. Returns the config, base url, and headers.'''

    # Load the config
    config = dotenv_values(".env")
    if not config: raise Exception("No .env config file found")


    # Get API base URL + token for selected NetX env
    netx_env = config["NETX_ENV"]

    if netx_env=="LIVE":
        netx_base_url = config["NETX_API_BASE_URL"]
        netx_api_token = config["NETX_API_TOKEN"]
    else:
        netx_base_url = config["TEST_NETX_API_BASE_URL"]
        netx_api_token = config["TEST_NETX_API_TOKEN"]


    # Set default HTTP headers
    headers = netx_api_setup_headers(headers, netx_api_token)

    return {'config': config, 'base_url':netx_base_url, 'headers': headers}


def netx_api_make_request(method:str=None, params:list=None, headers=None) -> dict:
    '''Makes a request to the NetX API'''
    
    json = netx_api_setup_json(method, params)

    netx_request = netx_api_setup_request(headers)

    uri = netx_request['base_url']
    headers = netx_request['headers']

    try:
        # NetX json-rpc API only permits POST ?
        r = requests.post(uri, json=json, headers=headers)
        r.raise_for_status()
        print(r.status_code)
        return r.json()

    except requests.exceptions.HTTPError as http_error:
        raise requests.exceptions.HTTPError("Could not " + method + " : " + http_error.response.text)


def netx_api_try_request(method, params, headers=None) -> dict:
    '''Tries a request to the NetX API, returns the HTTP status code 200/404/etc'''

    json = netx_api_setup_json(method, params)

    netx_request = netx_api_setup_request(headers)

    uri = netx_request['base_url']
    headers = netx_request['headers']

    try:
        r = requests.get(uri, json=json, headers=headers)
        return r.status_code

    except requests.exceptions.HTTPError as http_error:
        raise requests.exceptions.HTTPError("Could not " + method + " : " + http_error.response.text)


def netx_add_asset_to_folder(asset_id:int, folder_id:int, field_list:list=None):
    '''
    In NetX, Adds an asset to a folder via the NetX API
    - See method help: https://developer.netx.net/#getassetsbyfolder
    '''
    if field_list==None:
        field_list = [
            "asset.id",
            "asset.base",
            "asset.file",
            "asset.folders"
            ]

    method = 'addAssetToFolder'

    params = [
        asset_id, 
        folder_id,
        {"data": field_list}
        ]
    print(params)

    return netx_api_make_request(method, params)