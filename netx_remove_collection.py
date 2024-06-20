'''Remove assets via NetX API if they were unpublished/deleted in EMu'''

import logging
import re
import time
import xml.etree.ElementTree as ET
from utils import netx_api as un
from utils import xml_tools as ux
from utils import setup


def remove_group_from_netx(row:dict, current_netx_groups:list, live_or_test:str):
    '''Delete a given group, referenced by its name'''

    # In case API needs rate-limiting
    time.sleep(0.1)
    
    netx_match = []
    # netx_match = [group for group in netx_group_list['results'] if group['title'] == emu_row_netx_title]
    for group in current_netx_groups:
        # print(f"netx group title = {group['title']}")
        if len(re.findall(rf"^EMu - .+ - {row['irn']}$", group['title'])) > 0:
            netx_match.append(group['id'])
    # print(netx_match)

    

    # # Given Identifier/Filename, Get Asset ID
    # asset_data = un.netx_get_asset_by_field(
    #     search_field="IRN",
    #     search_value=row['irn'],
    #     data_to_get=['asset.id','asset.folders'],
    #     netx_test=live_or_test
    #     )


    try:

        # if 'result' not in asset_data or len(asset_data['result']['results']) < 1:
        #     log_skip = f'Skipping EMu irn {row["irn"]} - not found in NetX'
        #     print(log_skip)
        #     logging.info(log_skip)

        # else:
        #     asset_id = asset_data['result']['results'][0]['id']
        #     asset_folders = asset_data['result']['results'][0]['folders']
        #     asset_orig_folder_ids = [folder['id'] for folder in asset_folders]

        # Add asset to 'Remove_from_NetX' folder

        if len(netx_match) > 0:

            for netx_collection_id in netx_match:

                remove_group_log = un.netx_delete_collection(
                    collection_id = netx_collection_id,
                    netx_env=live_or_test
                    )

                if 'result' in remove_group_log:
                    log_message = f'NetX Collection {netx_collection_id} deleted'
                    print(log_message)
                    logging.info(log_message)

                else:
                    log_no_result = f'"result" not in updated NetX Asset {netx_collection_id}: {remove_group_log}'
                    print(log_no_result)
                    logging.error(log_no_result)


    except KeyError as err:
        err_message = f'ERROR - audit group data = {row}: Error = {err}'
        logging.error(err_message)

    return


def get_irns_to_remove(xml_element:ET.ElementTree) -> list:
    '''given xml records (as an ElementTree), return a list of record irns'''

    records_to_remove = []

    for record in xml_element:
        # New record

        prepped_record = {}
        for elem in record:

            if elem.tag == 'atom' and elem.text:
                if elem.attrib['name'] == 'AudKey':
                    prepped_record['irn'] = elem.text

                    if prepped_record['irn'] not in records_to_remove:
                        records_to_remove.append(prepped_record)

    return records_to_remove


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
    
    unpub_records_to_remove = []
    delete_records_to_remove = []
    
    try:

        unpub_input = full_xml_prefix + 'NetX_audit_unpublished_groups/' + input_date + '/xml*'
        unpub_input_path = f'Input unpublished-groups XML path = {unpub_input}'
        print(unpub_input_path)
        logging.info(unpub_input_path)

        delete_input = full_xml_prefix + 'NetX_audit_deleted_groups/' + input_date + '/xml*'
        delete_input_path = f'Input deleted-groups XML path = {delete_input}'
        print(delete_input_path)
        logging.info(delete_input_path)


        # Prep input-XML for unpub'ed & deleted IRNs
        unpub_xml = ux.get_input_xml(unpub_input, input_date)
        unpub_records_to_remove = get_irns_to_remove(unpub_xml)

        delete_xml = ux.get_input_xml(delete_input, input_date)
        delete_records_to_remove = get_irns_to_remove(delete_xml)


        # # Get existing NetX 'Remove_from_NetX' folder ID
        # remove_folder_data = un.netx_get_folder_by_path(
        #     folder_path="Remove_from_NetX",
        #     data_to_get=['folder.id'],
        #     netx_env=live_or_test
        #     )
        # if 'result' not in remove_folder_data:
        #     print(f'ERROR - {remove_folder_data}')
        #     logging.error(remove_folder_data)
        #     return

        # remove_folder_id = remove_folder_data['result']['id']


        # # smaller test-set
        # unpub_xml = unpub_xml[:10]
        # delete_xml = delete_xml[:10]

        
        # Get existing NetX collections IDs & titles
        netx_group_data = un.netx_get_collections(netx_env = live_or_test)
        
        if 'result' not in netx_group_data:
            print(f'ERROR with netx_get_collections - {netx_group_data}')
            logging.error(netx_group_data)
            return

        else:
           netx_group_list = netx_group_data['result']['results']



        records_to_remove = unpub_records_to_remove + delete_records_to_remove

        # print(f'records to remove:  {records_to_remove}')

        # Add assets to folders
        for row in records_to_remove:

            remove_group_from_netx(
                row = row,
                current_netx_groups = netx_group_list,
                live_or_test = live_or_test
                )

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
