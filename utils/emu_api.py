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

    # print(str(datetime.datetime.now()) + ' - starting check_resource')

    check_resource = emu_api_validate_resource(emu_table, emu_env)

    # print(str(datetime.datetime.now()) + ' - finishing check_resource')

    if check_resource == True:
        print(f'querying {emu_table}')
    
    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    if search_field is not None and search_value is not None:

        json_raw = {"AND":[{f"data.{search_field}":{operator:{"value": search_value }}}]}

    else:
        json_raw = {}

    # # NOTE - Would prefer to use urlencode() (not u.p.quote + re.sub), but can't get this to work:
    # json_prep = urlencode({k: json.dumps(v) for k, v in json_raw.items()}) 

    json_prep = urllib.parse.quote(str(json_raw))  
    json_prep = re.sub('%27', '%22', json_prep)  # NOTE - This is messed up, but it works.

    uri = base_url + emu_table + '?filter=' + json_prep

    r = requests.get(url=uri, headers=headers)  # , data=json_prep) # params=f'?filter={json_raw}',

    # print(str(datetime.datetime.now()) + ' - finishing GET')

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

    # print(str(datetime.datetime.now()) + ' - starting setup')

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + emu_table

    # print(str(datetime.datetime.now()) + ' - starting post')

    r = requests.post(url=uri, headers=headers, json=new_emu_record)

    # print(str(datetime.datetime.now()) + ' - finishing post')

    if r.status_code < 300:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json())}')


def emu_api_update_record(emu_table:str=None, emu_irn:int=None, emu_record:dict=None, emu_env:str=None):
    '''Update EMu record (specified by table + irn)'''

    # print(str(datetime.datetime.now()) + ' - starting setup')

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + emu_table + '/' + str(emu_irn)

    json_prep_list = []
    for k,v in emu_record.items():
        # TODO - reference field in schema to get correct path/value structure for atom/table/tec
        json_prep = {
            "op": "replace", "path":f'/{k}', "value": v
        }
        json_prep_list.append(json_prep)
    
    # print(str(datetime.datetime.now()) + ' - starting patch')

    r = requests.patch(url=uri, headers=headers, json=json_prep_list)

    # print(str(datetime.datetime.now()) + ' - finishing patch')

    if r.status_code < 300:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json())}')



def emu_api_get_media(mm_irn:str=None, category:str='media', emu_env:str=None):
    '''Retrieve specific (main) media file'''

    print(str(datetime.datetime.now()) + ' - starting setup')

    allowed_categories = ['media', 'resolution', 'supplementary']

    if category not in allowed_categories:
        raise Exception(f'Check category "{category}" - Must be one of {allowed_categories}')
    
    media_record = emu_api_query_numeric("emultimedia", "irn", "exact", mm_irn, emu_env)

    mime_type = media_record['matches'][0]['data']['MulMimeType']
    mime_format = media_record['matches'][0]['data']['MulMimeFormat']
    mulIdentifier = media_record['matches'][0]['data']['MulIdentifier']

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']
    config = emu_api_setup['config']

    uri = base_url + f'media/{mm_irn}:{category}:{mime_type}:{mime_format}:{mulIdentifier}'

    r = requests.get(url=uri, headers=headers)

    print(str(datetime.datetime.now()) + ' - finishing call')
    
    if r.status_code < 300:
        
        file_path = config['TEST_EMU_FILE_OUT'] + mulIdentifier
        file = open(file_path, "wb")
        file.write(r.content)
        file.close()

        return # r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json())}')


def emu_api_get_records_by_date_last_mod(
    emu_table:str=None, # 'eparties',
    search_field:str=None, # 'irn',
    operator:str='contains',  # exact
    search_value:str=None, # 1,
    emu_env:str=None
    ) -> dict:
    '''Retrieve specific EMu records by date last mod'''

    return


def emu_api_delete_record(emu_table:str=None, new_emu_record:dict=None, emu_env:str=None):
    '''Delete specific EMu record'''
    return