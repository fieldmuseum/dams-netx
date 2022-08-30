'''
Functions for using the NetX JSON-RPC API
- Based on dato_http_api.py functions
- NetX API docs - https://developer.netx.net
'''

import requests
import utils.setup as setup


def netx_api_setup_headers(headers:dict=None, netx_api_token:str=None) -> dict:
    '''Sets up the required default headers for using the NetX API. Allows for overriding the headers'''

    if headers is not None: return headers

    # Set up default headers
    headers = {
        'Authorization': 'apiToken ' + netx_api_token,
        'Content-Type': 'application/json'
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        # 'jsonrpc': '2.0', # 'X-Api-Version': '3',
        # 'id': '1234567890'
    }

    return headers


def netx_api_setup_request_body(method:str, params:list) -> dict:
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


def netx_api_setup_request(config:dict=None, headers:dict=None, netx_env:str=None) -> dict:
    '''Performs initial checks on a request. Returns the config, base url, and headers.'''

    # Load the config
    # config = dotenv_values(".env")
    if config is None:  
        config = setup.get_config_dams_netx()
        
        if not config:  
            raise Exception("No .env config file found")

    # Get API base URL + token for selected NetX env
    # netx_env = config["NETX_ENV"]
    if netx_env is None:
        netx_env == "TEST"

    if netx_env=="LIVE":
        netx_base_url = config["NETX_API_BASE_URL"]
        netx_api_token = config["NETX_API_TOKEN"]
    else:
        netx_base_url = config["TEST_NETX_API_BASE_URL"]
        netx_api_token = config["TEST_NETX_API_TOKEN"]


    # Set default HTTP headers
    headers = netx_api_setup_headers(headers=headers, netx_api_token=netx_api_token)

    return {'config': config, 'base_url':netx_base_url, 'headers': headers}


def netx_api_make_request(method:str=None, params:list=None, headers=None, netx_env:str=None) -> dict:
    '''Makes a request to the NetX API'''

    json = netx_api_setup_request_body(method=method, params=params)

    netx_request = netx_api_setup_request(headers=headers, netx_env=netx_env)
    # print(netx_request)

    uri = netx_request['base_url']
    headers = netx_request['headers']

    try:
        # NetX json-rpc API only permits POST ?
        r = requests.post(uri, json=json, headers=headers)
        r.raise_for_status()
        if r.status_code == 200:
            return r.json()
        else:
            print(f'Error - {r.status_code}')

    except requests.exceptions.HTTPError as http_error:
        raise requests.exceptions.HTTPError("Could not " + method + " : " + http_error.response.text)


def netx_api_try_request(method:str, params:dict, headers:dict=None, netx_env:str=None) -> dict:
    '''Tries a request to the NetX API, returns the HTTP status code 200/404/etc'''

    json = netx_api_setup_request_body(method, params)

    netx_request = netx_api_setup_request(headers=headers, netx_env=netx_env)

    uri = netx_request['base_url']
    headers = netx_request['headers']

    try:
        r = requests.get(uri, json=json, headers=headers)
        return r.status_code

    except requests.exceptions.HTTPError as http_error:
        raise requests.exceptions.HTTPError("Could not " + method + " : " + http_error.response.text)


def netx_remove_asset_from_folder(asset_id:int, folder_id:int, data_to_get:list=None, netx_env:str=None) -> dict:
    '''
    In NetX, Removes an asset from a folder via the NetX API
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#removeassetfromfolder
    '''

    if data_to_get==None:
        data_to_get = [
            "asset.id",
            "asset.base",
            "asset.file",
            "asset.folders"
            ]

    method = 'removeAssetFromFolder'

    params = [
        asset_id, 
        folder_id,
        {"data": data_to_get}
        ]
    # print(params)

    return netx_api_make_request(method, params, netx_env=netx_env)


def netx_add_asset_to_folder(asset_id:int, folder_id:int, data_to_get:list=None, netx_env:str=None) -> dict:
    '''
    In NetX, Adds an asset to a folder via the NetX API
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#addassettofolder
    '''

    if data_to_get==None:
        data_to_get = [
            "asset.id",
            "asset.base",
            "asset.file",
            "asset.folders"
            ]

    method = 'addAssetToFolder'

    params = [
        asset_id, 
        folder_id,
        {"data": data_to_get}
        ]
    # print(params)

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_folder_by_path(folder_path:str, data_to_get:list=None, netx_env:str=None) -> dict:
    '''
    Returns a dict that includes the NetX folder-id for a given NetX folder-path.
    - Also returns the folder name, description, path and child-folders.
    - See method help: https://developer.netx.net/#getfolderbypath
    '''

    if data_to_get==None:
        data_to_get = [
            "folder.id",
            "folder.base",
            "folder.children"
            ]

    method = 'getFolderByPath'

    params = [
        folder_path,
        {"data": data_to_get}
        ]
    # print(params)

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_asset_by_filename(file_name:str, data_to_get:list=['asset.id'], netx_env:str=None) -> dict:
    '''
    For a given filename, returns a dict that includes NetX asset.id (default).
    Other asset-data can be returned also/instead -- see https://developer.netx.net/#search.
    
    - NOTE - NetX getAssetsByQuery is more flexible, if this function should be more general.
    '''
    
    method = 'getAssetsByQuery'

    criteria = "exact"  # must be one of: 'exact', 'contains', 'range', 'folder', 'subquery'
    operator = "and"  # must be one of: "and", "or", "not"

    params = [
        {
            "query": [
                {
                    "operator": operator,
                    criteria: {
                        "field": "fileName",
                        "value": file_name
                    }
                }
            ]
        },
        {
            "data": data_to_get
        }
        ]
    # print(params)

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)

def netx_get_asset_by_field(field:str="fileChecksum", file_name:str=None, data_to_get:list=['asset.id'], netx_test:str=None) -> dict:
    '''
    For a given basic field and filename, returns a dict that includes NetX asset.id (default).
    Other asset-data can be returned also/instead -- see https://developer.netx.net/#search.
    
    - NOTE - NetX getAssetsByQuery is more flexible, if this function should be more general.
    '''
    
    method = 'getAssetsByQuery'

    netx_api_fields = [
        "assetId", "name",
        "fileChecksum", "fileName", "fileType", 
        "creationDate", "importDate", "modDate",
        "keywords"
        ]

    if field not in netx_api_fields:
        print('WARNING - check search field-name')

    criteria = "exact"  # must be one of: 'exact', 'contains', 'range', 'folder', 'subquery'
    operator = "and"  # must be one of: "and", "or", "not"

    params = [
        {
            "query": [
                {
                    "operator": operator,
                    criteria: {
                        "field": field,
                        "value": file_name
                    }
                }
            ]
        },
        {
            "data": data_to_get
        }
        ]
    # print(params)

    return netx_api_make_request(method=method, params=params, netx_test=netx_test)