'''Functions for using the NetX API'''
'''
DRAFT - nearly direct copy of dato-api; 
TO DO - line up functions with https://developer.netx.net
'''

import requests, time
from dotenv import dotenv_values


def netx_api_setup_request(json: dict, headers=None) -> dict:
    '''Performs initial checks on a request. Returns the config and headers.'''

    # Load the config
    config = dotenv_values(".env")
    if not config: raise Exception("No .env config file found")

    # Check that we have json record data
    if not json: raise Exception("No record json data has been provided")

    # Set default HTTP headers
    headers = netx_api_setup_headers(headers)

    return {'config': config, 'headers': headers}


def netx_api_setup_headers(headers=None) -> dict:
    '''Sets up the required default headers for using the NetX API. Allows for overriding the headers'''

    if headers is not None: return headers

    # Load the config
    config = dotenv_values(".env")
    if not config: raise Exception("No .env config file found")

    # Set up default headers
    headers = {
        'jsonrpc': '2.0', # 'X-Api-Version': '3',
        'X-Environment': config["NETX_ENVIRONMENT"],  # DATOCMS_ENV
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'apiToken': config["NETX_API_TOKEN"],  # 'Authorization': 'Bearer ' + config["NETX_API_TOKEN"],
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # If the DATOCMS_ENVIRONMENT is set to prod, remove the header
    # 'X-Environment' so the request is performed on the primary environment.
    if config["NETX_ENVIRONMENT"] == "prod":  # DATOCMS_ENV
        del headers["X-Environment"]

    return headers


def netx_api_make_request(method: str, uri: str, json=None, headers=None) -> dict:
    '''Makes a request to the NetX API'''

    try:
        if method.lower() == "get":
            r = requests.get(uri, json=json, headers=headers)
            r.raise_for_status()
            return r.json()
        if method.lower() == "post":
            r = requests.post(uri, json=json, headers=headers)
            r.raise_for_status()
            return r.json()
        if method.lower() == "put":
            r = requests.put(uri, json=json, headers=headers)
            r.raise_for_status()
            return r.json()
        if method.lower() == "delete":
            r = requests.delete(uri, headers=headers)
            r.raise_for_status()
            return r.json()
    except requests.exceptions.HTTPError as http_error:
        raise requests.exceptions.HTTPError("Could not " + method.upper() + " record: " + http_error.response.text)


def netx_api_try_request(uri: str, json=None, headers=None) -> dict:
    '''Tries a request to the NetX API, returns the HTTP status code 200/404/etc'''

    r = requests.get(uri, json=json, headers=headers)
    return r.status_code


def netx_add_asset_to_folder():
    '''In NetX, Adds an asset to a folder via the NetX API'''

    method = 'addAssetToFolder'

    netx_api_make_request('POST', method)