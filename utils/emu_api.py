'''
Functions for using texcdp (the EMu API)
- texrestapi docs - https://nexus.melbourne.axiell.com/texrestapi/latest/ 
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
    Returns a nested dict where dict['matches'] lists the current resources (EMu tables) available on the API
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


def emu_api_check_resource(emu_table:str=None, emu_env:str=None):
    '''Returns True if an input resource exists on the API'''

    if emu_table is None:
        raise Exception(f'Check emu_table -- it should be a string (e.g. "ecatalogue"), not None')

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


def emu_api_get_schema(emu_table:str=None, emu_env:str=None):
    '''
    Returns a nested dict with the schema and field-types for a given EMu table.
    '''

    if emu_table is None or len(emu_table) < 1:
        raise Exception(f'Check emu_table -- it should be a valid table-name as a string (e.g. "ecatalogue"), not None or ""')

    if emu_env is None:
        emu_env = "TEST"

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + 'resources/' + emu_table

    # print(f'header = {headers}')
    # print(f'uri = {uri}')

    r = requests.get(url=uri, headers=headers)

    if r.status_code < 300:
        return r.json()
    else:
        raise Exception(f'Check API & config - API response status code {r.status_code} | text: {str(r.json())}')

def emu_api_check_field_type(
    emu_table:str=None, # 'eparties',
    emu_field:str=None, # 'AdmDateLastModified',
    emu_env:str=None
    ) -> dict:
    '''
    Returns data-type (e.g. 'string' or 'array') and data-foramt (e.g. 'integer' or 'partial-date') for a given table & column
    '''

    table_schema = emu_api_get_schema(emu_table=emu_table, emu_env=emu_env)

    emu_field = re.sub(r'_tab$|0$', '', emu_field)

    # Setup list of grouped fields
    if 'properties' in table_schema['data']:
        full_field_list = table_schema['data']['properties'].keys()
        group_field_dict = {}
        for field in full_field_list:
            if field.find('_grp') > 0:
                subgroup_fields = list(table_schema['data']['properties'][field]['items']['properties'].keys())
                for subgroup_field in subgroup_fields:
                    group_field_dict[subgroup_field] = field

    # Check EMu table schema for field
    if emu_field in full_field_list:
        table_field_props = table_schema['data']['properties'][emu_field]
    
    # Also check grouped fields if no match initially found
    elif emu_field in group_field_dict.keys():
        group = group_field_dict[emu_field]
        table_field_props = table_schema['data']['properties'][group]['items']['properties'][emu_field]

    else:
        raise Exception(f'Check EMu field {emu_field} & table {emu_table} - field not found in table or groups {group_field_dict.values()}.')

    field_type = table_field_props['type']
    if 'format' in table_field_props.keys():
        field_type = re.sub(r'^partial\-', '', table_field_props['format'])
        field_type = re.sub(r'^uri$', 'integer', field_type)

    # mode = search_field_type  # should be one of ["date", "time", "latitude", "longitude"]

    # allowed_field_types = ['date', 'time', 'integer', 'float', 'latitude', 'longitude']

    # if search_field_type not in allowed_field_types:
    #     raise Exception(f'Check search_field "{search_field}" (type "{search_field_type}") - Must be one of {allowed_field_types}')

    return field_type


def emu_api_query_text(
    emu_table:str=None, # 'eparties',
    search_field:str=None, # 'irn',
    operator:str='contains',  # exact
    search_value_single:str=None, # 1,
    search_value_range:list=None,
    emu_env:str=None
    ) -> dict:
    '''
    Queries texcdp for search field/value, and returns a nested dict where dict['matches'] is the list of matching records.
    For search_value_range, format input as [min,max]. 
    - For "greater than" ranges, use [min,None]; 
    - For "less than" ranges, use [None,max]
    - For date-ranges, format as "YYYY-MM-DD"
    '''

    # print(str(datetime.datetime.now()) + ' - starting check_resource')

    check_resource = emu_api_check_resource(emu_table, emu_env)

    # print(str(datetime.datetime.now()) + ' - finishing check_resource')

    # if check_resource == True:
    #     print(f'querying {emu_table}')
    
    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    if search_field is not None:
        search_field_type = emu_api_check_field_type(emu_table=emu_table, emu_field=search_field)

        if search_value_range is not None:

            if type(search_value_range) is not list:
                raise Exception(f'Check search_value_range {search_value_range} - It should be a list like so: [min, max]')

            allowed_field_types = ['date', 'time', 'integer', 'float', 'latitude', 'longitude']

            # for value in search_value_range:
            #     if value is not None:
            #         if type(value) != search_field_type:
            #             raise Exception(f'Check range values in {search_value_range} - They should be {search_field_type} for field {search_field}')

            if search_field_type not in allowed_field_types:
                raise Exception(f'Check search_field {search_field} - for range-search, type {search_field_type} is not in allowed types {allowed_field_types}')
            else:
                print(f'getting {search_field_type} range for {search_value_range} in {emu_table}.{search_field}')

            
            range = {}
            if search_value_range[1] is None:
                if search_value_range[0] is None:
                    raise Exception(f'Check search_value_range {search_value_range} - It should be a list like so: [min, max]')
                range["gte"] = search_value_range[0]

            elif search_value_range[0] is None:
                range["lte"] = search_value_range[1]

            else:
                range["gte"] = search_value_range[0]
                range["lte"] = search_value_range[1]
            
            # Add optional mode property
            if search_value_range[0] is not None:
                check_mode = search_value_range[0]
            else: 
                check_mode = search_value_range[1]
            if re.match(r'\d{4}\-\d{2}\-\d{2}', check_mode) is not None:
                range["mode"] = "date"

            # print(range)
            json_raw = {"AND":[{f"data.{search_field}":{"range":range}}]}


        elif search_value_single is not None:

            print(f'getting {search_field_type} {search_value_single} in {emu_table}.{search_field}')

            json_raw = {"AND":[{f"data.{search_field}":{operator:{"value": search_value_single }}}]}


    else:  json_raw = {}

    # # NOTE - Would prefer to use urlencode() (not u.p.quote + re.sub), but can't get this to work:
    # json_prep = urlencode({k: json.dumps(v) for k, v in json_raw.items()}) 

    json_prep = urllib.parse.quote(str(json_raw))  
    json_prep = re.sub('%27', '%22', json_prep)  # NOTE - This is messed up, but it works.

    uri = base_url + emu_table + '?filter=' + json_prep

    # print(f'uri = {uri}')

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
    search_value_single:str=None, # '1',
    search_value_range:str=None,
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
    
    return emu_api_query_text(
        emu_table=emu_table, 
        search_field=search_field, 
        operator=operator, 
        search_value_single=search_value_single,
        search_value_range=search_value_range,
        emu_env=emu_env)


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


def emu_api_delete_record(emu_table:str=None, new_emu_record:dict=None, emu_env:str=None):
    '''Delete specific EMu record'''
    return