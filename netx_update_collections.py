'''Update NetX collections/groups of assets via NetX API if corresponding groups were edited in EMu'''

import logging
import re
import time
import xml.etree.ElementTree as ET
from utils import netx_api as un
from utils import xml_tools as ux
from utils import setup


def check_asset_in_netx(emu_irn:str, live_or_test:str):
    ''' For a given EMu irn, check/get corresponding NetX ID '''

    asset_id = None

    # In case API needs rate-limiting
    time.sleep(0.5)

    # Given Identifier/Filename, Get Asset ID
    asset_data = un.netx_get_asset_by_field(
        search_field = "IRN",
        search_value = emu_irn,
        data_to_get = ['asset.id'],
        netx_test = live_or_test
        )

    try:

        if 'result' not in asset_data or len(asset_data['result']['results']) < 1:
            log_skip = f'Skipping EMu irn {emu_irn} - not found in NetX'
            print(log_skip)
            logging.info(log_skip)

        else:
            asset_id = asset_data['result']['results'][0]['id']

    except KeyError as err:
        err_message = f'ERROR - asset_data = {asset_data}: Error = {err}'
        logging.error(err_message)

    return asset_id


def get_groups_to_update(xml_element:ET.ElementTree, live_or_test) -> list:
    '''given xml records (as an ElementTree), return a list of Group-records & grouped MM assetIDs'''

    groups_to_update = []

    # # smaller set
    # xml_element = xml_element[3:6]

    for record in xml_element:
        # New record

        prepped_record = {}

        # prepped_record['irn'] = ''
        # prepped_record['title'] = ''
        # prepped_record['type'] = ''
        # prepped_record['owner'] = ''

        for elem in record:

            if elem.attrib['name'] == 'GroupType':
                if elem.text != 'Static':
                    continue

            # Get the Group IRN, Title, type, UserId
            if elem.tag == 'atom' and elem.text:
                if elem.attrib['name'] == 'irn':
                    prepped_record['irn'] = elem.text                    

                if elem.attrib['name'] == 'GroupName':
                    prepped_record['title'] = elem.text
                    
                if elem.attrib['name'] == 'GroupType':
                    prepped_record['type'] = elem.text
                    
                if elem.attrib['name'] == 'UserId':
                    prepped_record['owner'] = elem.text
                    
                                        

            # Get a list of MM_irns in the group
            if elem.tag == 'table' and elem.text:
                if prepped_record['type'] == 'Static':
                    if elem.attrib['name'] == 'Keys_tab':

                        mm_irn_list = []
                        netx_id_list = []

                        # # smaller test-set
                        # elem = elem[:6]
                        print(f'LEN OF ELEM = {len(elem)}')
                        
                        for row in elem:
                            # print(f'row = {row}')
                            # print(f'row text = {row.text}')
                            if row.tag == 'tuple':
                                for subrow in row:
                                    if subrow.attrib['name'] == 'Keys' and subrow.text:
                                        print(f'MM irn = {subrow.text}')
                                        mm_irn_list.append(subrow.text)

                                        # retrieve NetX assetID by 'IRN' attribute
                                        netx_id = check_asset_in_netx(
                                            emu_irn = subrow.text,
                                            live_or_test=live_or_test
                                            )
                                        
                                        if netx_id is not None:
                                            netx_id_list.append(netx_id)
                        
                        prepped_record['mm_irn_list'] = mm_irn_list
                        prepped_record['netx_id_list'] = netx_id_list
                
                        # NOTE - Consider:
                        #   1 - Checking if all EMu MM irn's are in NetX collection
                        #   2 - If not all in, merge NetX/EMu lists, update NetX coll.
                        # 
                        #   For now, skipping & only controlling group content via EMu

        if prepped_record not in groups_to_update:
            if prepped_record['type'] == 'Static':
                groups_to_update.append(prepped_record)

    return groups_to_update


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test, input_date = setup.get_sys_argv(2)

    config = setup.get_config_dams_netx(live_or_test)

    full_xml_prefix = setup.get_path_from_env(
        live_or_test,
        config['ORIGIN_PATH_XML'],
        config['TEST_ORIGIN_PATH_XML']
        )
    

    try:

        # Prep input-XML for groups       
        groups_input = full_xml_prefix + 'NetX_groups/' + input_date + '/xml*'
        groups_input_path = f'Input groups XML path = {groups_input}'
        print(groups_input_path)
        logging.info(groups_input_path)

        # Get list of EMu group records
        groups_xml = ux.get_input_xml(groups_input, input_date)
        groups_to_check_in_netx = get_groups_to_update(groups_xml, live_or_test)

        # Get existing NetX collections IDs & titles
        netx_group_data_raw = un.netx_get_collections(netx_env = live_or_test)
        
        if 'result' not in netx_group_data_raw:
            print(f'ERROR with netx_get_collections - {netx_group_data_raw}')
            logging.error(netx_group_data_raw)
            return

        else:
           list_size = netx_group_data_raw['result']['size']
           netx_group_data = un.netx_get_collections(netx_env = live_or_test, size = list_size)
           netx_group_list = netx_group_data['result']
           # netx_group_title_list = [row['title'] for row in netx_group_list]


        # # smaller test-set
        # groups_to_check_in_netx = groups_to_check_in_netx[:2]

        # Add assets to folders

        for emu_row in groups_to_check_in_netx:

            emu_row_netx_title_old = f"EMu - {emu_row['title']} - {emu_row['irn']}"
            emu_row_netx_title = f"EMu - {emu_row['title']} - {emu_row['irn']} - {emu_row['owner']}"
            print(f"EMu group title in NetX:  {emu_row_netx_title}")

            netx_match = []
            for group in netx_group_list['results']:
                if group['title'] == emu_row_netx_title_old:
                    netx_match.append(group)
                elif group['title'] == emu_row_netx_title:
                    if group not in netx_match:
                        netx_match.append(group)

            if len(netx_match) > 0:

                # Use first matching group in NetX
                # # TODO - Check for duplicates?
                print(netx_match[0]['title'])

                netx_match_id = netx_match[0]['id']
            
                # if f"EMu - {emu_row['title']} - {emu_row['irn']}" == netx_row['title']:

                # print(f'emu_row = {emu_row["title"]}')
                # print(f'netx_row = {netx_row["title"]}')

                updated_coll = un.netx_update_collection(
                    collection_id = netx_match_id,
                    collection_title = emu_row_netx_title,
                    asset_id_list = emu_row['netx_id_list'],
                    data_to_get = None,
                    netx_env = live_or_test
                    )
                
                if 'result' not in updated_coll:
                    print(f'ERROR with netx_update_collection - {updated_coll}')
                    logging.error(updated_coll)
                    return

                else:
                    updated_coll_id = updated_coll['result']['id']                  
                    print(f'Updated existing collection - collId {updated_coll_id}')
                    

            else:

                print(f"Adding: {emu_row_netx_title}")
                print(emu_row['netx_id_list'])
                
                new_coll = un.netx_create_collection(
                    collection_title = emu_row_netx_title,
                    asset_id_list = emu_row['netx_id_list'],
                    data_to_get = None,
                    netx_env = live_or_test
                    )
                
                if 'result' not in new_coll:
                    print(f'ERROR with netx_create_collection - {new_coll}')
                    logging.error(new_coll)
                    return

                else:
                    new_coll_id = new_coll['result']['id']                  
                    print(f'Added new collection - collId {new_coll_id}')

                # print(f'Added new collection -  {new_coll}')

        # except KeyError as err:
        #     log_err = f'ERROR - {remove_folder_data} -- {err}'
        #     print(log_err)
        #     logging.error(log_err)
    
    except IndexError as index_err:
        log_index_err = f'ERROR - check for empty input NetX_audit XML dirs on input-date {input_date} - {index_err}'
        print(log_index_err)
        logging.error(log_index_err)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
