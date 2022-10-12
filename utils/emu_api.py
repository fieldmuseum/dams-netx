'''
Functions for using texcdp (the EMu API)
- texcdp docs - https://nexus.melbourne.axiell.com/texcdp/latest
- Reminder: set 'EMU' variables in your .env (see '.env.example')
'''

import datetime, re, requests
from urllib.parse import urlencode
import utils.setup as setup


def emu_api_get_token(
    config:dict=None, 
    user_id:str=None, 
    user_pw:str=None, 
    base_uri:str=None
    ) -> dict:
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

    uri = base_uri + "tokens"
    
    r = requests.post(url=uri, headers=headers, json=json)

    if r.status_code == 201:
        return r.headers['Authorization']  # json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {r.text}')


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
        # print(f'emu_api_token = {emu_api_token}')
        # token_prepped = re.sub(r'.*/tokens/', '', emu_api_token)  # ['id'])
        # print(f'token = {token_prepped}')
        headers['Authorization'] = emu_api_token  # str(emu_api_token['id'])

    return headers


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
        base_uri = config["EMU_API_BASE_URL"]
    else:
        base_uri = config["TEST_EMU_API_BASE_URL"]


    emu_api_token = emu_api_get_token(base_uri=base_uri)

    # Set default HTTP headers
    headers = emu_api_setup_headers(headers=headers, emu_api_token=emu_api_token)

    return {'config': config, 'base_url':base_uri, 'headers': headers, 'token': emu_api_token}


def emu_api_get_resources(emu_env:str=None):
    '''Get a list of current resources available on the API'''

    if emu_env is None:
        emu_env = "TEST"

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    # config = emu_api_setup['config']
    # token = emu_api_setup['token']
    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + 'resources'

    print(f'header = {headers}')
    print(f'uri = {uri}')

    r = requests.get(url=uri, headers=headers)

    if r.status_code == 201:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {r.text}')


def emu_api_query_general(
    emu_table:str='eparties',
    search_field:str=None, # 'irn',
    operator:str='contains',
    search_value:str=None,
    emu_env:str=None
    ) -> dict:
    '''Queries texp for search field/value, and returns a dict of results'''
    '''TODO - Try search_field/value as list instead of str'''
    
    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    if search_field is not None and search_value is not None:

        json = {
            "OR": [
                {f'data.{search_field}': { operator: {'value': search_value }}}
            ]
        }

    else:
        json = {}
    
    print(f'json = {json}')

    uri = base_url + emu_table + '?filter=' + str(json) # + '&limit=10&cursorType=file'

    print(f'header = {headers}')
    print(f'json = {json}')
    print(f'uri = {uri}')


    r = requests.get(url=uri, headers=headers)  # json=json, 

    if r.status_code < 300:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json)}')
