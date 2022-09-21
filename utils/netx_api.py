'''
Functions for using the NetX JSON-RPC API
- Based on dato_http_api.py functions
- NetX API docs - https://developer.netx.net
'''

import datetime, re, requests
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
    # print(json)

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

def netx_get_asset_by_field(
    search_field:str="fileChecksum", 
    search_value:str=None, 
    data_to_get:list=['asset.id'], 
    netx_test:str=None,
    criteria:str='exact'
    ) -> dict:
    '''
    For a given basic/system field and value, returns a dict that includes NetX asset.id (default).
     - To search by a NetX system field, use camel case, e.g. "assetId" or "fileName"
     - To search by a custom attribute, match the frontend case, e.g. "IRN" or "Other Number"
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

    field_or_attribute = "field"

    if search_field not in netx_api_fields:
        print(f'WARNING - check search field-name {search_field}')
        field_or_attribute = "attribute"
    
    elif re.match(r".*Date$", search_field) is not None:
        search_value = convert_date_for_netx(search_value)

    netx_api_criteria = [
        "exact", "contains"  # , "range", "folder", "subquery"
        ]
    
    if criteria is None:
        criteria = "exact"  # must be one of: 'exact', 'contains', 'range', 'folder', 'subquery'

    elif criteria not in netx_api_criteria:
        print(f'WARNING - check search criteria {criteria}')

    operator = "and"  # must be one of: "and", "or", "not"

    params = [
        {
            "query": [
                {
                    "operator": operator,
                    criteria: {
                        field_or_attribute: search_field,
                        "value": search_value
                    }
                }
            ]
        },
        {
            "page": {
                "startIndex":0,
                "size": 10
            },
            "data": data_to_get
        }
        ]
    # print(params)

    check = netx_api_make_request(method=method, params=params, netx_env=netx_test)

    if check is not None:
        if 'result' in check.keys():
            param_size = check['result']['size']
            if param_size > 200:
                print(f'adjusting orig param_size to 200; full results size is {param_size}')
                param_size = 200
            params[1]['page']['size'] = param_size

    return netx_api_make_request(method=method, params=params, netx_env=netx_test)


def netx_get_asset_by_range(
    search_field:str="modDate", 
    search_min:str=None, 
    search_max:str=None, 
    data_to_get:list=['asset.id'],  #  'asset.attributes'], 
    netx_test:str=None,
    ) -> dict:
    '''
    For a given basic/system range-field and value, 
    returns a dict that includes NetX asset.id (default).
    Other asset-data can be returned also/instead -- see https://developer.netx.net/#search.

    Leave the 'search_max' / 'search_min' value blank for greater than / less than searches.
    '''
    
    method = 'getAssetsByQuery'

    netx_api_fields = [
        "assetId", "name",
        "fileChecksum", "fileName", "fileType", 
        "creationDate", "importDate", "modDate",
        "keywords"
        ]

    field_or_attribute = "field"

    if search_field not in netx_api_fields:
        print(f'WARNING - check search field-name {search_field}')
        field_or_attribute = "attribute"
    
    elif re.match(r".*Date$", search_field) is not None:
        if search_min is not None:
            search_min = convert_date_for_netx(search_min)
        if search_max is not None:
            search_max = convert_date_for_netx(search_max)

    # operator = "and"  # must be one of: "and", "or", "not"

    params = [
        {
            "query": [
                {
                    "operator": "and",
                    "range": {
                        field_or_attribute: search_field,
                        "min": search_min,
                        "max": search_max,
                        "includeMin": False,
                        "includeMax": False
                    }
                }
            ]
        },
        {
            "page": {
                "startIndex":0,
                "size": 10
            },
            "data": data_to_get
        }
        ]
    # print(params)

    check = netx_api_make_request(method=method, params=params, netx_env=netx_test)

    if check is not None:
        if 'result' in check.keys():
            param_size = check['result']['size']
            if param_size > 200:
                print(f'adjusting orig param_size to 200; full results size is {param_size}')
                param_size = 200
            params[1]['page']['size'] = param_size

    return netx_api_make_request(method=method, params=params, netx_env=netx_test)



def netx_delete_asset(asset_id:int, netx_env:str=None) -> dict:
    '''
    CAREFUL: In NetX, Deletes an asset via the NetX API
    - Returns an empty object.
    - See method help: https://developer.netx.net/#removeassetfromfolder
    '''

    method = 'deleteAsset'

    params = [
        asset_id
        ]
    # print(params)

    return netx_api_make_request(method, params, netx_env=netx_env)


def convert_date_for_netx(date_string_raw:str) -> str:
    '''
    Convert a date-string from a "YYYY-M-D" format to NetX's preferred milliseconds-since-epoch
    '''

    epoch = datetime.datetime.utcfromtimestamp(0)

    # parse H:M:S from date-string, if present
    if re.match(r'.*\s+\d{1,2}:\d{1,2}(:\d{1,2})*', date_string_raw) is not None:
        time_string_raw = re.sub(r'(.*)(\s+)(\d{1,2}:\d{1,2}(:\d{1,2})*)', r'\g<3>', date_string_raw)
        date_string_raw = re.sub(r'(.*)(\s+)(\d{1,2}:\d{1,2}(:\d{1,2})*)', r'\g<1>', date_string_raw)
    else:
        time_string_raw:str='00:00:00'

    # check date-formate
    if not re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_string_raw): 
        raise Exception(f'Input date {date_string_raw} is not formatted in "YYYY-MM-DD"')
    
    date_time_string = f'{date_string_raw} {time_string_raw}'

    # re-format input date from string 'YYYY-MM-DD' to datetime-object
    # # https://pythonguides.com/convert-a-string-to-datetime-in-python/ 
    date_ymd = datetime.datetime.strptime(date_time_string, '%Y-%m-%d %H:%M:%S')

    print(date_ymd)

    return str(int((date_ymd - epoch).total_seconds() * 1000))
