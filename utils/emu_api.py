'''
Functions for using texcdp (the EMu API)
- texrestapi docs - https://nexus.melbourne.axiell.com/texrestapi/latest/ 
- Reminder: set 'EMU' variables in your .env (see '.env.example')
'''

import datetime
import re
import urllib.parse
# import logging
# import http.client as http_client
import requests
from utils import setup

# # Uncomment to log at debug-level
# http_client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

def emu_api_get_token(
    config:dict=None,
    user_id:str=None,
    user_pw:str=None,
    # base_uri:str=None,
    emu_env:str='TEST'
    ) -> dict:
    '''Retrieves a JWT token from texcdp'''

    # Load the config
    if config is None:
        config = setup.get_config_dams_netx()

        if not config:
            raise Exception("No .env config file found")

    # Get API base URL + token for selected NetX env
    # if emu_env is None:
    #     emu_env == "TEST"

    emu_env = config["EMU_ENV"]

    if emu_env=="LIVE":
        base_uri = config["EMU_API_BASE_URL"]

        if user_id is None:
            user_id = config["EMU_API_ID"]

        if user_pw is None:
            user_pw = config["EMU_API_PW"]

    else:
        base_uri = config["TEST_EMU_API_BASE_URL"]

        if user_id is None:
            user_id = config["TEST_EMU_API_ID"]

        if user_pw is None:
            user_pw = config["TEST_EMU_API_PW"]


    json = {
        "username":user_id,
        "password":user_pw
    }

    headers = emu_api_setup_headers()

    uri = base_uri + "tokens"

    r = requests.post(
        url=uri,
        headers=headers,
        json=json,
        timeout=60,
        )

    if r.status_code == 201:
        # print(r.headers['Authorization'])
        return r.headers['Authorization']  # json()

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )

def emu_api_delete_tokens(
        config:dict=None,
        headers:dict=None,
        token_to_delete:str=None,
        emu_env:str='TEST'
        ):
    '''
    Deletes all of a user's tokens
    https://help.emu.axiell.com/emurestapi/latest/04-Resources-Tokens.html
    DELETE /{tenant}/tokens
    '''

    # Load the config
    if config is None:
        config = setup.get_config_dams_netx()

        if not config:
            raise Exception("No .env config file found")

    emu_env = config["EMU_ENV"]

    if emu_env=="LIVE":
        base_uri = config["EMU_API_BASE_URL"]

        # if user_id is None:
        #     user_id = config["EMU_API_ID"]

        # if user_pw is None:
        #     user_pw = config["EMU_API_PW"]

    else:
        base_uri = config["TEST_EMU_API_BASE_URL"]

        # if user_id is None:
        #     user_id = config["TEST_EMU_API_ID"]

        # if user_pw is None:
        #     user_pw = config["TEST_EMU_API_PW"]


    # json = {
    #     "username":user_id,
    #     "password":user_pw
    # }

    if headers is None:
        headers = emu_api_setup_headers()

    uri = base_uri + "tokens"

    if token_to_delete is not None:
        uri = base_uri + "tokens/" + token_to_delete

    # print(uri)

    r = requests.delete(
        url=uri,
        headers=headers,
        # json=json,
        timeout=10,
        )

    if r.status_code < 301:
        # print(f'token deleted: {r.text}')
        return

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


def emu_api_setup_headers(headers:dict=None, emu_api_token:dict=None) -> dict:
    '''
    Sets up the required default headers for using the texrestapi.
    Allows for overriding the headers
    '''

    if headers is not None:
        return headers

    # Set up default headers
    headers = {
        'Content-Type': 'application/json',
        'Prefer': 'representation=minimal'
    }

    if emu_api_token is not None:
        # print(f'adding emu_api_token to header: {emu_api_token}')
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
    if emu_env=="LIVE":
        base_uri = config["EMU_API_BASE_URL"]
    else:
        emu_env = "TEST"
        base_uri = config["TEST_EMU_API_BASE_URL"]


    emu_api_token = emu_api_get_token(emu_env=emu_env)  # base_uri=base_uri,

    # Set default HTTP headers
    headers = emu_api_setup_headers(headers=headers, emu_api_token=emu_api_token)

    return {'config': config, 'base_url':base_uri, 'headers': headers}


def emu_api_get_resources(emu_env:str=None):
    '''
    Returns a nested dict where dict['matches'] lists 
    the current resources (EMu tables) available on the API.
    '''

    if emu_env is None:
        emu_env = "TEST"

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + 'resources'

    # print(f'header = {headers}')
    # print(f'uri = {uri}')

    r = requests.get(
        url=uri,
        headers=headers,
        timeout=10,
        )

    if r.status_code < 300:
        return r.json()

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


def emu_api_check_resource(emu_table:str=None, emu_env:str=None):
    '''Returns True if an input resource exists on the API'''

    if emu_table is None:
        raise Exception(
            'Check emu_table -- it should be a string (e.g. "ecatalogue"), not None'
            )

    resource_tables = []
    check_resources = emu_api_get_resources(emu_env=emu_env)
    if 'matches' in check_resources.keys():
        if len(check_resources['matches']) > 0:
            for resource in check_resources['matches']:
                resource_table = re.sub(r'(.+/)*', '', resource['id'])
                resource_tables.append(resource_table)

    if emu_table not in resource_tables:
        raise Exception(
            f'Check emu_table {emu_table} -- not in list of texcdp resources {resource_tables}'
            )

    return True


def emu_api_get_schema(emu_table:str=None, emu_env:str=None):
    '''
    Returns a nested dict with the schema and field-types for a given EMu table.
    '''

    if emu_table is None or len(emu_table) < 1:
        raise Exception(
            'Check emu_table -- enter a valid table-name (e.g. "eparties"), not None or ""'
            )

    if emu_env is None:
        emu_env = "TEST"

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + 'resources/' + emu_table

    # print(f'header = {headers}')
    # print(f'uri = {uri}')

    r = requests.get(
        url=uri,
        headers=headers,
        timeout=10)
    print(r.status_code)

    if r.status_code < 300:
        return r.json()

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


def emu_api_check_field_type(
    emu_table:str=None, # 'eparties',
    emu_field:str=None, # 'AdmDateLastModified',
    emu_env:str=None
    ) -> dict:
    '''
    Returns data-type (e.g. 'string' or 'array') and data-foramt 
    (e.g. 'integer' or 'partial-date') for a given table & column
    '''

    table_schema = emu_api_get_schema(emu_table=emu_table, emu_env=emu_env)

    emu_field = re.sub(r'_tab$|0$', '', emu_field)

    # Setup list of grouped fields
    if 'properties' in table_schema['data']:
        full_field_list = table_schema['data']['properties'].keys()
        # print(f'full field list: {full_field_list}')

        group_field_dict = {}
        for field in full_field_list:
            if field.find('_grp') > 0:
                subgroup_fields = list(
                    table_schema['data']['properties'][field]['items']['properties'].keys()
                    )
                for subgroup_field in subgroup_fields:
                    group_field_dict[subgroup_field] = field

    # Check EMu table schema for field
    if emu_field in full_field_list:
        table_field_props = table_schema['data']['properties'][emu_field]

    # Also check grouped fields if no match initially found
    elif emu_field in group_field_dict:
        group = group_field_dict[emu_field]
        table_field_props = table_schema['data']['properties'][group]['items']['properties'][emu_field]

    else:
        raise Exception(
            f'Check EMu field {emu_field} & table {emu_table} - field not found in table or groups {group_field_dict.values()}.'
            )

    field_type = table_field_props['type']
    if 'format' in table_field_props.keys():
        field_type = re.sub(r'^partial\-', '', table_field_props['format'])
        field_type = re.sub(r'^uri$', 'integer', field_type)

    # mode = search_field_type  # should be one of ["date", "time", "latitude", "longitude"]

    # allowed_field_types = ['date', 'time', 'integer', 'float', 'latitude', 'longitude']

    # if search_field_type not in allowed_field_types:
    #     raise Exception(f'Check search_field "{search_field}" (type "{search_field_type}")
    #        - Must be one of {allowed_field_types}')

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

    # check_resource = emu_api_check_resource(emu_table, emu_env)

    # # print(str(datetime.datetime.now()) + ' - finishing check_resource')

    # if check_resource == True:
    #     print(f'querying {emu_table}')

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']
    json_raw = {}
    # print(f'headers = {headers}')

    if search_field is not None:
        # print(f'checking field type for {emu_table}.{search_field}')
        search_field_type = emu_api_check_field_type(
            emu_table=emu_table, emu_field=search_field, emu_env=emu_env
            )

        if search_value_range is not None:

            if not isinstance(search_value_range, list):
                raise Exception(
                    f'Check that search_value_range {search_value_range} is a list: [min, max]'
                    )

            allowed_field_types = ['date', 'time', 'integer', 'float', 'latitude', 'longitude']

            # for value in search_value_range:
            #     if value is not None:
            #         if type(value) != search_field_type:
            #             raise Exception(f'Check range values in {search_value_range} 
            #               - They should be {search_field_type} for field {search_field}')

            if search_field_type not in allowed_field_types:
                raise Exception(
                    f'Check search_field {search_field} - for range-search, type {search_field_type} is not in allowed types {allowed_field_types}'
                    )
            else:
                print(
                    f'getting {search_field_type} range for {search_value_range} in {emu_table}.{search_field}'
                    )

            search_range = {}
            if search_value_range[1] is None:
                if search_value_range[0] is None:
                    raise Exception(f'Check search_value_range {search_value_range} - It should be a list like so: [min, max]')
                search_range["gte"] = search_value_range[0]

            elif search_value_range[0] is None:
                search_range["lte"] = search_value_range[1]

            else:
                search_range["gte"] = search_value_range[0]
                search_range["lte"] = search_value_range[1]

            # Add optional mode property
            if search_value_range[0] is not None:
                check_mode = search_value_range[0]
            else: 
                check_mode = search_value_range[1]
            if re.match(r'\d{4}\-\d{2}\-\d{2}', check_mode) is not None:
                search_range["mode"] = "date"

            # print(search_range)
            json_raw = {"AND":[{f"data.{search_field}":{"range":search_range}}]}


        elif search_value_single is not None:

            print(
                f'getting {search_field_type} {search_value_single} in {emu_table}.{search_field}'
                )

            json_raw = {"AND":[{f"data.{search_field}":{operator:{"value": search_value_single }}}]}

    # # NOTE - Would prefer to use urlencode() (not u.p.quote + re.sub), but can't get this to work:
    # json_prep = urlencode({k: json.dumps(v) for k, v in json_raw.items()}) 

    json_prep = urllib.parse.quote(str(json_raw))  
    json_prep = re.sub('%27', '%22', json_prep)  # NOTE - This is messed up, but it works.

    uri = base_url + emu_table + '?filter=' + json_prep

    r = requests.get(
        url=uri,
        headers=headers,
        timeout=10
        )  # , data=json_prep) # params=f'?filter={json_raw}',

    # delete token
    emu_api_delete_tokens(config=None, headers=headers, emu_env=emu_env)

    if r.status_code < 300:
        return r.json()

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


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


def emu_api_get_record_by_irn(
    emu_table:str=None, # 'eparties',
    search_field:str='irn',
    operator:str='exact',  # contains
    search_value_single:str=None, # '1',
    emu_env:str=None
    ) -> dict:
    '''
    Queries texcdp for an irn in a specified table, and returns a nested dict 
    where dict['matches'] is the list of matching records.
    '''

    allowed_ops = ['exact', 'exists', 'range']

    if operator not in allowed_ops:
        raise Exception(f'Check operator "{operator}" - Must be one of {allowed_ops}')

    return emu_api_query_text(
        emu_table=emu_table, 
        search_field=search_field, 
        operator=operator, 
        search_value_single=search_value_single,
        emu_env=emu_env)


def emu_api_add_record(emu_table:str=None, new_emu_record:dict=None, emu_env:str=None):
    '''Add a new EMu record, given a json dict of EMu fields:values for the given EMu table'''

    # print(str(datetime.datetime.now()) + ' - starting setup')

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + emu_table

    # print(str(datetime.datetime.now()) + ' - starting post')

    r = requests.post(url=uri, headers=headers, json=new_emu_record, timeout=10)

    # print(str(datetime.datetime.now()) + ' - finishing post')

    # delete token
    emu_api_delete_tokens(config=None, headers=headers, emu_env=emu_env)


    if r.status_code < 300:
        return r.json()

    raise Exception(
    f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
    )


def emu_api_update_record(
        emu_table:str=None,
        emu_irn:int=None,
        operation:str='add',
        emu_record:dict=None,
        emu_env:str=None
        ):
    '''
    Update EMu record (specified by table + irn)

    (from https://help.emu.axiell.com/emurestapi/latest/05-Appendices-Patch.html )
        Allowed 'operation' values include: 
            - add, replace, remove, copy, move
    '''

    # print(str(datetime.datetime.now()) + ' - starting setup')

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']

    uri = base_url + emu_table + '/' + str(emu_irn)

    json_prep_list = []
    for k,v in emu_record.items():
        # TO DO - reference field in schema to get correct path/value structure for atom/table/tec
        json_prep = {
            "op": operation, "path":f'/{k}', "value": v
        }
        json_prep_list.append(json_prep)

    # print(str(datetime.datetime.now()) + ' - starting patch')

    r = requests.patch(url=uri, headers=headers, json=json_prep_list, timeout=100)

    # print(str(datetime.datetime.now()) + ' - finishing patch')

    # delete token
    emu_api_delete_tokens(config=None, headers=headers, emu_env=emu_env)

    if r.status_code < 300:

        return r.json()

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


def emu_api_get_media(mm_irn:str=None, category:str='media', emu_env:str=None):
    '''Retrieve specific (main) media file'''

    print(str(datetime.datetime.now()) + ' - starting setup')

    allowed_categories = ['media', 'resolution', 'supplementary']

    if category not in allowed_categories:
        raise Exception(f'Check category "{category}" - Must be one of {allowed_categories}')

    media_record = emu_api_get_record_by_irn("emultimedia", "irn", "exact", mm_irn, emu_env)

    print(media_record['matches'][0]['data'].keys())

    mime_type = media_record['matches'][0]['data']['MulMimeType']
    mime_format = media_record['matches'][0]['data']['MulMimeFormat']

    mul_identifier = None
    if 'MulIdentifier' in media_record['matches'][0]['data'].keys():
        mul_identifier = media_record['matches'][0]['data']['MulIdentifier']

    if mul_identifier is None:
        print(f'No file found for IRN {mm_irn}')
        return

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']
    config = emu_api_setup['config']

    uri = base_url + f'media/{mm_irn}:{category}:{mime_type}:{mime_format}:{mul_identifier}'

    r = requests.get(url=uri, headers=headers, timeout=100)

    print(str(datetime.datetime.now()) + ' - finishing call')

    # delete token
    emu_api_delete_tokens(config=None, headers=headers, emu_env=emu_env)

    if r.status_code < 300:

        file_path = config['TEST_EMU_FILE_OUT'] + mul_identifier
        file = open(file_path, "wb")
        file.write(r.content)
        file.close()

        return

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


def emu_api_ingest_media(mm_irn:int, media_file_path:str, emu_env:str=None):
    '''Ingest a media file to an EMu Multimedia record'''

    print(str(datetime.datetime.now()) + ' - starting setup')

    # Check if record exists
    media_record = emu_api_get_record_by_irn("emultimedia", "irn", "exact", mm_irn, emu_env)

    # Check if it already includes a main file
    # mime_type = media_record['matches'][0]['data']['MulMimeType']
    # mime_format = media_record['matches'][0]['data']['MulMimeFormat']
    if len(media_record['matches']) > 0:
        if 'MulIdentifier' in media_record['matches'][0]['data']:
            mul_identifier = media_record['matches'][0]['data']['MulIdentifier']
            print(f'Overwriting existing file in MM irn {mm_irn} : {mul_identifier}')

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']
    # config = emu_api_setup['config']

    uri = base_url + f'media/{mm_irn}'

    prepped_file = {"file":media_file_path}

    r = requests.put(url=uri, headers=headers, json=prepped_file, timeout=100)

    print(str(datetime.datetime.now()) + ' - finishing call')

    # delete token
    emu_api_delete_tokens(config=None, headers=headers, emu_env=emu_env)

    if r.status_code < 300:

        # print(f'Status :  {r.status_code}')
        # print(f'Adding file. {r.content}')
        # print(f'Headers :  {r.headers}')
        # print(f'Request :  {r.request}')
        # print(f'Reason :  {r.reason}')

        return

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


def emu_api_ingest_media_http(mm_irn:int, media_path:str, media_name:str, emu_env:str=None):
    '''Ingest a remote media file (using HTTP multipart mode) to an EMu Multimedia record'''

    print(str(datetime.datetime.now()) + ' - starting setup')

    # # Check if record exists
    # media_record = emu_api_get_record_by_irn("emultimedia", "irn", "exact", mm_irn, emu_env)

    # # Check if it already includes a main file
    # # mime_type = media_record['matches'][0]['data']['MulMimeType']
    # # mime_format = media_record['matches'][0]['data']['MulMimeFormat']
    # if len(media_record['matches']) > 0:
    #     if 'MulIdentifier' in media_record['matches'][0]['data']:
    #         mul_identifier = media_record['matches'][0]['data']['MulIdentifier']
    #         print(f'Overwriting existing file in MM irn {mm_irn} : {mul_identifier}')

    emu_api_setup = emu_api_setup_request(emu_env=emu_env)

    base_url = emu_api_setup['base_url']
    headers = emu_api_setup['headers']
    headers.pop('Content-Type')  # requests needs to set this.

    uri = base_url + f'media/{mm_irn}'

    prepped_file = {"file": open(media_path+media_name, 'rb')}

    # print(headers)
    # print(uri)

    r = requests.put(url=uri, headers=headers, files=prepped_file, timeout=1000)

    print(str(datetime.datetime.now()) + ' - finishing call')

    # delete token
    emu_api_delete_tokens(config=None, headers=headers, emu_env=emu_env)

    if r.status_code < 300:

        # print(f'Status :  {r.status_code}')
        # print(f'Adding file. {r.content}')
        # print(f'Headers :  {r.headers}')
        # print(f'Request :  {r.request}')
        # print(f'Reason :  {r.reason}')

        return

    raise Exception(
        f'Check API & config - response status code {r.status_code} | {r.reason} | text: {r.text}'
        )


# def emu_api_delete_record(emu_table:str=None, new_emu_record:dict=None, emu_env:str=None):
#     '''Delete specific EMu record'''
#     return
