'''
Functions for using the NetX JSON-RPC API
- Based on dato_http_api.py functions
- NetX API docs - https://developer.netx.net
'''

import datetime
import re
import requests
import utils.setup as setup


def netx_api_setup_headers(headers:dict=None, netx_api_token:str=None) -> dict:
    '''
    Sets up the required default headers for using the NetX API.
    Allows for overriding the headers
    '''

    if headers is not None:
        return headers

    # Set up default headers
    headers = {
        'Authorization': 'apiToken ' + netx_api_token,
        # 'Content-Type': 'application/json'
        # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36
        #               (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        # 'jsonrpc': '2.0', # 'X-Api-Version': '3',
        # 'id': '1234567890'
    }

    return headers


def netx_api_setup_request_body(method:str=None, params:list=None) -> dict:
    '''Sets up the required request object format for the NetX API.'''

    # # Check that method is defined (not required for 'import' methods)
    # if not method: raise Exception("No NetX API method has been provided")

    # # Check that we have json record data
    # if params is None: raise Exception("No NetX API parameter data has been provided")

    # Setup request-object
    request_object = {
        'jsonrpc': '2.0', # 'X-Api-Version': '3',
        'id': '1234'}

    if method is not None:
        request_object['method'] = method,  # e.g. "getAssets"

    request_object['params'] = params   # list of [record-ids] and {'data' : ['fields']}

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
        netx_env = "TEST"

    if netx_env=="LIVE":
        netx_base_url = config["NETX_API_BASE_URL"]
        netx_api_token = config["NETX_API_TOKEN"]
    else:
        netx_base_url = config["TEST_NETX_API_BASE_URL"]
        netx_api_token = config["TEST_NETX_API_TOKEN"]


    # Set default HTTP headers
    headers = netx_api_setup_headers(headers=headers, netx_api_token=netx_api_token)

    return {'config': config, 'base_url':netx_base_url, 'headers': headers}


def netx_api_make_request(
        method:str=None,
        params:list=None,
        headers=None,
        netx_env:str=None,
        uri_suffix:str=None,
        request:str=None,
        body:dict=None,
        file=None
        ) -> dict:
    '''Makes a request to the NetX API'''

    json = None

    if params is not None:
        json = netx_api_setup_request_body(method=method, params=params)
    # # print(json)
    # elif file is not None:
    #     json = json['params'][0]
    #     json['file'] = file

    netx_request = netx_api_setup_request(headers=headers, netx_env=netx_env)
    # print(netx_request)

    if uri_suffix is None:
        uri = netx_request['base_url'] + 'rpc/'
    else:
        uri = netx_request['base_url'] + uri_suffix

    if method is None:
        method = ''

    headers = netx_request['headers']

    netx_call = None

    try:
        if request is None:
            netx_call = requests.post
        elif request.lower() == 'put':
            netx_call = requests.put

        if file is None and body is None:
            r = netx_call(uri, json=json, headers=headers)
        else:
            files = {'file': open(file, 'rb')}
            r = netx_call(uri, data=body, files=files, headers=headers)

        r.raise_for_status()

    except requests.exceptions.HTTPError as http_error:
        raise requests.exceptions.HTTPError(
            f"Could not use method {method} : {http_error.response.text}"
            )
    except requests.RequestException as e:
        print(f"Error requesting data from {uri} : {e}")

    return r.json()


def netx_api_try_request(method:str, params:dict, headers:dict=None, netx_env:str=None) -> dict:
    '''Tries a request to the NetX API, returns the HTTP status code 200/404/etc'''

    json = netx_api_setup_request_body(method, params)

    netx_request = netx_api_setup_request(headers=headers, netx_env=netx_env)

    uri = netx_request['base_url']
    headers = netx_request['headers']

    try:
        r = requests.get(uri, json=json, headers=headers, timeout=(45,90))
        return r.status_code

    except requests.exceptions.HTTPError as http_error:
        raise requests.exceptions.HTTPError(
            f"Could not use method {method} : {http_error.response.text}"
            )


def netx_remove_asset_from_folder(
        asset_id:int,
        folder_id:int,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, Removes an asset from a folder via the NetX API
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#removeassetfromfolder
    '''

    if data_to_get is None:
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

    return netx_api_make_request(method, params, netx_env=netx_env)


def netx_add_asset_to_folder(
        asset_id:int,
        folder_id:int,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, Adds an asset to a folder via the NetX API
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#addassettofolder
    '''

    if data_to_get is None:
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

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_folder_by_path(folder_path:str, data_to_get:list=None, netx_env:str=None) -> dict:
    '''
    Returns a dict that includes the NetX folder-id for a given NetX folder-path.
    - Also returns the folder name, description, path and child-folders.
    - See method help: https://developer.netx.net/#getfolderbypath
    '''

    if data_to_get is None:
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

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_create_collection(
        collection_title:str,
        asset_id_list:list,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, create a collection of listed assets via the NetX API
    - Also returns the collections's id, name, and number of assets.
    - See method help: https://developer.netx.net/#createcollection
    '''

    if data_to_get is None:
        data_to_get = [
            "collection.id",
            "collection.base",
            "collection.permissions"
            ]

    method = 'createCollection'

    params = [
        {"title": collection_title},
        asset_id_list,
        {"data": data_to_get}
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_delete_collection(collection_id:str=None, netx_env:str=None) -> dict:
    '''
    In NetX, delete ONE collection by its ID via the NetX API
    - Also returns the collections's id, name, and number of assets.
    - See method help: https://developer.netx.net/#getcollection
    '''

    # if data_to_get is None:
    #     data_to_get = [
    #         "collection.id",
    #         "collection.base",
    #         "collection.permissions"
    #         ]

    method = 'deleteCollection'

    params = [
        collection_id
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_collection(collection_id:str=None, data_to_get:list=None, netx_env:str=None) -> dict:
    '''
    In NetX, get ONE collection by its ID via the NetX API
    - Also returns the collections's id, name, and number of assets.
    - See method help: https://developer.netx.net/#getcollection
    '''

    if data_to_get is None:
        data_to_get = [
            "collection.id",
            "collection.base",
            "collection.permissions"
            ]

    method = 'getCollection'

    params = [
        collection_id,
        {"data": data_to_get}
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_collections(data_to_get:list=None, netx_env:str=None, size:int=None) -> dict:
    '''
    In NetX, get ALL of a user's readable collections via the NetX API
    - Also returns the collections's id, name, and number of assets.
    - See method help: https://developer.netx.net/#getcollections
    '''

    if data_to_get is None:
        data_to_get = [
            "collection.id",
            "collection.base",
            # "collection.permissions"
            ]

    if size is None:
        size = 8

    method = 'getCollections'

    params = [
        {
            "page": {
                "startIndex": 0,
                "size": size
                },
            "data": data_to_get}
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_collections_by_user(
        user_id:int,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, get collections to which a user has at least Viewer access
    - Also returns the collections's id, name, number of assets, permissions.
    - See method help: https://developer.netx.net/#getcollectionsbyuser
    '''

    # if data_to_get is None:
    #     data_to_get = [
    #         "collection.id",
    #         "collection.base",
    #         "collection.permissions"
    #         ]

    method = 'getCollectionsByUser'

    params = [user_id, None]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_update_collection(
        collection_id:int,
        collection_title:str,
        asset_id_list:list,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, update a collection via the NetX API
    - Also returns the collections's id, name, and number of assets.
    - See method help: https://developer.netx.net/#updatecollection
    '''

    if data_to_get is None:
        data_to_get = [
            "collection.id",
            "collection.base",
            # "collection.permissions"
            ]

    method = 'updateCollection'

    params = [
        {
            "id": collection_id,
            "title": collection_title
        },
        asset_id_list,
        {"data": data_to_get}
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_assets_by_collection(
        collection_id:int,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, update a collection via the NetX API
    - Also returns the collections's id, name, and number of assets.
    - See method help: https://developer.netx.net/#getassetsbycollection
    '''

    if data_to_get is None:
        data_to_get = [
            "asset.id"
            ]

    method = 'getAssetsByCollection'

    params = [
        collection_id,
        {"data": data_to_get}
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_asset_by_filename(
        file_name:str,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    For a given filename, returns a dict that includes NetX asset.id (default).
    Other asset-data can be returned also/instead -- see https://developer.netx.net/#search.

    - NOTE - NetX getAssetsByQuery is more flexible, if this function should be more general.
    '''

    if data_to_get is None:
        data_to_get = [
            "asset.id"
            ]

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
    data_to_get:list=None,
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

    if data_to_get is None:
        data_to_get = [
            "asset.id"
            ]

    method = 'getAssetsByQuery'

    netx_api_fields = [
        "assetId", "name",
        "fileChecksum", "fileName", "fileType",
        "creationDate", "importDate", "modDate",
        "keywords"
        ]

    field_or_attribute = "field"

    if search_field not in netx_api_fields:
        field_or_attribute = "attribute"

    elif re.match(r".*Date$", search_field) is not None:
        search_value = convert_date_for_netx(search_value)

    netx_api_criteria = [
        "exact", "contains"  # , "range", "folder", "subquery"
        ]

    if criteria not in netx_api_criteria:
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
    data_to_get:list=None,
    netx_test:str=None,
    ) -> dict:
    '''
    For a given basic/system range-field and value,
    returns a dict that includes NetX asset.id (default).
    Other asset-data can be returned also/instead -- see https://developer.netx.net/#search.

    Leave the 'search_max' / 'search_min' value blank for greater than / less than searches.
    '''
    if data_to_get is None:
        data_to_get = [
            "asset.id"
            ]

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
            if param_size > 1000:
                print(f'adjusting orig param_size to 200; full results size is {param_size}')
                param_size = 1000
            params[1]['page']['size'] = param_size

    return netx_api_make_request(method=method, params=params, netx_env=netx_test)


def netx_update_asset(
        # asset_id:int,
        data_to_update:dict,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, Update an asset via the NetX API
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#updateasset
    '''

    if data_to_update is None or not isinstance(data_to_update, dict):
        raise Exception(
            f'Check data_to_update {data_to_update} - Input should be dict of netx-fields:values'
            )

    if 'id' not in data_to_update.keys():
        raise Exception(
            f'Check data_to_update {data_to_update} - first key/value should be id:[netx-asset-id]'
            )

    if data_to_get is None or len(data_to_get) < 1:
        data_to_get = [
            "asset.id",
            "asset.base",
            "asset.file",
            "asset.folders"
            ]

    method = 'updateAsset'

    params = [
        data_to_update,
        {"data": data_to_get}
        ]
    # print(params)

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_delete_asset(asset_id:int, netx_env:str=None) -> dict:
    '''
    CAREFUL: In NetX, Deletes an asset via the NetX API
    - Returns an empty object.
    - See method help: https://developer.netx.net/#deleteasset
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

    # epoch = datetime.datetime.utcfromtimestamp(0)
    epoch = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)

    # parse H:M:S from date-string, if present
    if re.match(r'.*\s+\d{1,2}:\d{1,2}(:\d{1,2})*', date_string_raw) is not None:
        time_string_raw = re.sub(
            r'(.*)(\s+)(\d{1,2}:\d{1,2}(:\d{1,2})*)(.*)',
            r'\g<3>',
            date_string_raw
            )

        date_string_raw = re.sub(
            r'(.*)(\s+)(\d{1,2}:\d{1,2}(:\d{1,2})*)(.*)',
            r'\g<1>',
            date_string_raw
            )

        # print(f'time string: {time_string_raw}')
        # print(f'date string: {date_string_raw}')
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


def netx_import_asset(folder_id:int,
                      filepath:str,
                      filename:str,
                      netx_env:str=None
                      ) -> dict:
    '''
    In NetX, Imports a new asset via the NetX API, and returns its NetX asset ID if succesful.
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#import-asset
    '''

    uri_suffix = 'import/asset'

    # # Add file to request
    # files = {'file': open(filepath+filename, 'rb')}
    # r = requests.post(url, files=files,
    #                   data={'folderId':folder_id, 'fileName':filename},
    #                   headers={'Authorization': 'apiToken {sTuffNjunk}')

    method = None

    file_data = {
        # 'file':open(filepath + filename, 'rb'),
        'folderId':folder_id,
        'fileName':filename
    }

    file_to_upload = filepath+filename

    with open(filepath + filename, 'rb'): # as f:
        r = netx_api_make_request(
            method=method,
            netx_env=netx_env,
            uri_suffix=uri_suffix,
            body=file_data,
            file=file_to_upload
            )

    return r


def netx_reimport_asset(
        asset_id:int,
        filepath:str,
        filename:str,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, Reimports an existing asset via the NetX API
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#reimport-asset
    '''

    uri_suffix = f'import/asset/{asset_id}'

    method = None  # 'addAssetToFolder'

    file_to_upload = {
        'file':open(filepath + filename, 'rb'),
        'fileName':filename
    }

    # requests.put(files=)

    if data_to_get is None:
        data_to_get = [
            "asset.id",
            "asset.base",
            "asset.file",
            "asset.folders"
            ]

    params = [
        file_to_upload,
        {"data": data_to_get}
        ]

    # with open(file_to_upload['file'], 'rb') as f:
    #     r = netx_api_make_request(method=method,
    #                               params=params, netx_env=netx_env,
    #                               uri_suffix=uri_suffix, request='put')

    return netx_api_make_request(
        method=method,
        params=params,
        netx_env=netx_env,
        uri_suffix=uri_suffix,
        request='put'
        )


def netx_version_asset(
        asset_id:int,
        filename:str,
        data_to_get:list=None,
        netx_env:str=None
        ) -> dict:
    '''
    In NetX, Imports a new version of an existing asset via the NetX API
    - Also returns the asset's id, name, filename, and folders.
    - See method help: https://developer.netx.net/#version-asset
    '''

    uri_suffix = f'import/asset/{asset_id}/version'

    method = None  # 'addAssetToFolder'

    file_to_upload = {
        'fileName':filename
    }


    if data_to_get is None:
        data_to_get = [
            "asset.id",
            "asset.base",
            "asset.file",
            "asset.folders"
            ]

    params = [
        file_to_upload,
        {"data": data_to_get}
        ]
    # print(params)

    return netx_api_make_request(
        method=method,
        params=params,
        netx_env=netx_env,
        uri_suffix=uri_suffix
        )


def netx_import_view(asset_id:int,
                     filepath:str,
                     filename:str,
                     viewname:str=None,
                     description:str=None,
                     netx_env:str=None) -> dict:
    '''
    In NetX, Imports a new view and adds it to an existing asset via the NetX API.
    Returns its NetX asset ID if succesful.(?)
    - Also returns the view's asset-id, name, filename, and folders.
    - See method help: https://developer.netx.net/#import-view
    '''

    uri_suffix = f'import/asset/{asset_id}/view'

    method = None  # 'addAssetToFolder'

    file_data = {
        # 'file':open(filepath + filename, 'rb'),
        'fileName':filename,
        'viewName':viewname,
        'description':description
    }

    file_to_upload = filepath+filename

    with open(filepath + filename, 'rb'): # as f:
        r = netx_api_make_request(
            method=method,
            netx_env=netx_env,
            uri_suffix=uri_suffix,
            body=file_data,
            file=file_to_upload
            )

    return r


def netx_get_groups_by_user(user_id:str, paging:list=None, netx_env:str=None) -> dict:
    '''
    For a given user ID, returns a list of NetX group IDs and names.
    The 'paging' argument should be a list of start-number, and results per page
    e.g. [0,30] starts for the first (0) result, and includes 30 results per page.
    Paging can also be set -- see https://developer.netx.net/#getgroupsbyuser
    '''

    method = 'getGroupsByUser'

    if paging is None:
        paging = [0,30]

    params = [
        user_id,
        {
            "page": {
                "startIndex": paging[0],
                "size": paging[1]
            }
        }
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_users_by_group(group_id:str, paging:list=None, netx_env:str=None) -> dict:
    '''
    For a given group ID, returns a list of NetX user IDs, levels, and names.
    The 'paging' argument should be a list of start-number, and results per page
    e.g. [0,30] starts for the first (0) result, and includes 70 results per page.
    Paging can also be set -- see https://developer.netx.net/#getusersbygroup
    '''

    method = 'getUsersByGroup'

    if paging is None:
        paging = [0,70]

    params = [
        group_id,
        {
            "page": {
                "startIndex": paging[0],
                "size": paging[1]
            }
        }
        ]

    return netx_api_make_request(method=method, params=params, netx_env=netx_env)


def netx_get_self(netx_env:str=None) -> dict:
    '''
    In NetX, gets user id of current api user
    - See method help: https://developer.netx.net/#getself
    '''

    # if data_to_get is None:
    #     data_to_get = [
    #         "asset.id",
    #         "asset.base",
    #         "asset.file",
    #         "asset.folders"
    #         ]

    method = 'getSelf'

    params = [
        None
        # asset_id,
        # folder_id,
        # {"data": data_to_get}
        ]

    return netx_api_make_request(
        method=method,
        params=params,
        netx_env=netx_env
        )
