'''
Functions for using texcdp (the EMu API)
- texcdp docs - https://nexus.melbourne.axiell.com/texcdp/latest
- Reminder: set 'EMU' variables in your .env (see '.env.example')
'''

import datetime, json, re, requests, urllib.parse
import urllib.parse
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
        'Content-Type': 'application/json',
        'Prefer': 'representation=minimal'
    }

    if emu_api_token is not None:
        headers['Authorization'] = emu_api_token

    return headers


def emu_api_setup_request(config:dict=None, headers:dict=None, emu_env:str=None) -> dict:
    '''Performs initial checks on a request. Returns the config, base url, and headers.'''

    # Load the config
    if config is None:  
        config = setup.get_config_dams_netx()
        
        if not config:  
            raise Exception("No .env config file found")

    # Get API base URL + token for selected NetX env
    if emu_env is None:
        emu_env == "TEST"

    if emu_env=="LIVE":
        base_uri = config["EMU_API_BASE_URL"]
    else:
        base_uri = config["TEST_EMU_API_BASE_URL"]


    emu_api_token = emu_api_get_token(base_uri=base_uri)

    # Set default HTTP headers
    headers = emu_api_setup_headers(headers=headers, emu_api_token=emu_api_token)

    return {'config': config, 'base_url':base_uri, 'headers': headers}


def emu_api_get_resources(emu_env:str=None):
    '''
    Returns a nested dict where dict['matches'] is the current resources (EMu tables) available on the API
    '''

    if emu_env is None:
        emu_env = "TEST"

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + 'resources'

    # print(f'header = {headers}')
    # print(f'uri = {uri}')

    r = requests.get(url=uri, headers=headers)

    if r.status_code < 300:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json())}')


def emu_api_validate_resource(emu_table:str=None, emu_env:str=None):
    '''Returns True if an input resource exists on the API'''

    resource_tables = []
    check_resources = emu_api_get_resources(emu_env=emu_env)
    if 'matches' in check_resources.keys():
        if len(check_resources['matches']) > 0:
            for resource in check_resources['matches']:
                resource_table = re.sub(r'(.+/)*', '', resource['id'])
                resource_tables.append(resource_table)
    
    if emu_table not in resource_tables:
        raise Exception(f'Check emu_table {emu_table} -- not in list of texcdp resources {resource_tables}')
    
    else: return True


def emu_api_query_text(
    emu_table:str=None, # 'eparties',
    search_field:str=None, # 'irn',
    operator:str='contains',  # exact
    search_value:str=None, # 1,
    emu_env:str=None
    ) -> dict:
    '''
    Queries texcdp for search field/value, and returns a nested dict where dict['matches'] is the list of matching records
    TODO - Try search_field/value as list instead of str
    '''

    check_resource = emu_api_validate_resource(emu_table, emu_env)

    if check_resource == True:
        print(f'querying {emu_table}')
    
    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    if search_field is not None and search_value is not None:

        json_raw = {"AND":[{f"data.{search_field}":{operator:{"value": search_value }}}]}

        # # NOTE - Would prefer to use urlencode() (not u.p.quote + re.sub), but can't get this to work:
        # json_prep = urlencode({k: json.dumps(v) for k, v in json_raw.items()}) 

        json_prep = urllib.parse.quote(str(json_raw))  
        json_prep = re.sub('%27', '%22', json_prep)  # NOTE - This is messed up, but it works.

    else:
        json_prep = {}

    uri = base_url + emu_table + '?filter=' + json_prep

    r = requests.get(url=uri, headers=headers)  # , data=json_prep)

    if r.status_code < 300:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json())}')


def emu_api_query_numeric(
    emu_table:str=None, # 'eparties',
    search_field:str=None, # 'irn',
    operator:str='exact',  # contains
    search_value:str=None, # '1',
    emu_env:str=None
    ) -> dict:
    '''
    Queries texcdp for numeric search field/value, and returns a nested dict 
    where dict['matches'] is the list of matching records
    TODO - Try search_field/value as list instead of str
    '''

    allowed_ops = ['exact', 'exists', 'range']

    if operator not in allowed_ops:
        raise Exception(f'Check operator "{operator}" - Must be one of {allowed_ops}')
    
    return emu_api_query_text(emu_table, search_field, operator, search_value, emu_env)


def emu_api_add_record(emu_table:str=None, new_emu_record:dict=None, emu_env:str=None):
    '''Add a new EMu record, given a json dict of EMu fields:values for the given EMu table'''

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + emu_table

    r = requests.post(url=uri, headers=headers, json=new_emu_record)

    if r.status_code < 300:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json())}')
        

def emu_api_update_record():
    '''Update EMu record (specified by table + irn)'''
    return


def emu_api_get_records_by_date_last_mod():
    '''Retrieve specific EMu records by date last mod'''
    return