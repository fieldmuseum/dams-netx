'''Remove assets via NetX API if they were unpublished/deleted in EMu'''

import glob
import logging
import time
import xml.etree.ElementTree as ET
from utils import netx_api as un
from utils import setup


def remove_from_netx(row:dict, remove_folder:int, live_or_test:str):
    '''
    For a given asset's filename, pathMove asset
    to the 'Remove_from_NetX' folder
    [remove from all other folders]
    '''

    # In case API needs rate-limiting
    time.sleep(0.1)

    # Given Identifier/Filename, Get Asset ID
    asset_data = un.netx_get_asset_by_filename(
        row['file'],
        data_to_get=['asset.id','asset.folders'],
        netx_env=live_or_test
        )

    # if 'result' not in asset_data or len(asset_data['result']['results']) < 1:
    #     logging.error(asset_data)
    #     return

    try:
        asset_id = asset_data['result']['results'][0]['id']
        asset_folders = asset_data['result']['results'][0]['folders']
        asset_orig_folder_ids = [folder['id'] for folder in asset_folders]

        # Add asset to 'Remove_from_NetX' folder
        remove_asset_log = un.netx_add_asset_to_folder(
            asset_id=asset_id,
            folder_id=remove_folder,
            data_to_get=[],
            netx_env=live_or_test
            )

        if 'result' in remove_asset_log:
            folders = [folder['path'] for folder in remove_asset_log['result']['folders']]
            asset = remove_asset_log['result']['file']['name']
            log_message = f'{asset} - folders updated to: {folders}'
            print(log_message)
            # row['status'] = remove_asset_log['result']
            logging.info(log_message)

        else:
            print(f'ERROR - {remove_asset_log}')
            # row['status'] = remove_asset_log
            logging.error(remove_asset_log)


        for folder_id in asset_orig_folder_ids:
            if folder_id is not remove_folder:

                un.netx_remove_asset_from_folder(
                    asset_id=asset_id,
                    folder_id=folder_id
                    )

                log_message = f'Asset {asset_id} removed from folder {folder_id}'
                print(log_message)
                logging.info(log_message)

            else:
                log_error = f'Cannot remove Asset {asset_id} from Folder {folder_id}'
                logging.error(log_error)


    except KeyError as err:
        err_message = f'ERROR - asset_data = {asset_data}: Error = {err}'
        logging.error(err_message)


    # # Remove asset from all but 'Remove from NetX' folder
    # remove_asset_log = un.netx_remove_asset_from_folder(
    #     asset_id=asset_id,
    #     folder_id = folder_id,
    #     netx_env=live_or_test
    #     )


    # # # Add Asset to 'Remove from NetX' Folder -- https://developer.netx.net/#addassettofolder
    # folder_id = folder_id_list['Remove from NetX']
    # # folder_data = un.netx_add_asset_to_folder(asset_id, folder_id, netx_env=live_or_test)

    # if 'result' in remove_asset_log:
    #     folders = [folder['path'] for folder in remove_asset_log['result']['folders']]
    #     asset = remove_asset_log['result']['file']['name']
    #     log_message = f'{asset} - folders updated to: {folders}'
    #     print(log_message)
    #     # row['status'] = remove_asset_log['result']
    #     logging.info(log_message)

    # else:
    #     print(f'ERROR - {remove_asset_log}')
    #     # row['status'] = remove_asset_log
    #     logging.error(remove_asset_log)

    return


# def get_unique_folder_id_list(path_add_rows:list, live_or_test:str):
#     '''
#     Given a pathAdd CSV, retrieve folder IDs for a unique list of folder-names
#     Return a list of {folder_name:folder_id}
#     '''

#     unique_folders = []

#     for row in path_add_rows:

#         if row['pathAdd'] not in unique_folders:
#             unique_folders.append(row['pathAdd'])

#     folder_id_list = {}

#     if len(unique_folders) > 0:
#         for folder_name in unique_folders:

#             # Get Asset's Secondary Departments
#             folder_data = un.netx_get_folder_by_path(
#                 folder_path=folder_name,
#                 data_to_get=None,
#                 netx_env=live_or_test
#                 )

#             # if 'result' not in folder_data:
#             #     print(f'ERROR - {folder_data}')
#             #     logging.error(folder_data)
#             #     return

#             try:
#                 folder_id = folder_data['result']['id']
#                 folder_id_list[folder_name] = folder_id

#             except KeyError as err:
#                 err = f'ERROR - {folder_data}'
#                 logging.error(err)

#     return folder_id_list


def get_irns_to_remove(xml_element:ET.ElementTree) -> list:
    '''given xml records (as an ElementTree), return a list of record irns'''

    records_to_remove = []

    for record in xml_element:
        # New record

        prepped_record = {}
        for elem in record:

            if elem.tag == 'atom' and elem.text:
                if elem.attrib['name'] == 'irn':
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

    unpub_input = full_xml_prefix + 'NetX_audit_unpublished_MM/' + input_date + '/xml*'
    unpub_input_path = f'Input unpublished-MM XML path = {unpub_input}'
    print(unpub_input_path)
    logging.info(unpub_input_path)

    unpub_file_log = f'Input unpublished-MM XML file = {glob.glob(unpub_input)[0]}'
    print(unpub_file_log)
    logging.info(unpub_file_log)


    delete_input = full_xml_prefix + 'NetX_audit_deleted_MM/' + input_date + '/xml*'
    delete_input_path = f'Input deleted-MM XML path = {delete_input}'
    print(delete_input_path)
    logging.info(delete_input_path)

    delete_file_log = f'Input deleted-MM XML file = {glob.glob(delete_input)[0]}'
    print(delete_file_log)
    logging.info(delete_file_log)

    remove_folder_data = un.netx_get_folder_by_path(
        folder_path="Remove_from_NetX",
        data_to_get=['folder.id'],
        netx_env=live_or_test
        )
    if 'result' not in remove_folder_data:
        print(f'ERROR - {remove_folder_data}')
        logging.error(remove_folder_data)
        return

    try:
        remove_folder_id = remove_folder_data['result']['id']

    except KeyError as err:
        err = f'ERROR - {remove_folder_data}'
        logging.error(err)

    try:

        remove_folder_id = remove_folder_data['result']['id']

        # Import Event & Catalog exports too
        unpub_xml = ET.ElementTree().parse(glob.glob(unpub_input)[0])
        delete_xml = ET.ElementTree().parse(glob.glob(delete_input)[0])

        # # smaller test-set
        # unpub_xml = unpub_xml[:10]
        # delete_xml = delete_xml[:10]

        unpub_records_to_remove = get_irns_to_remove(unpub_xml)
        delete_records_to_remove = get_irns_to_remove(delete_xml)
        records_to_remove = unpub_records_to_remove + delete_records_to_remove

        # Add assets to folders
        for row in records_to_remove:
            remove_from_netx(
                row=row,
                remove_folder=remove_folder_id,
                live_or_test=live_or_test
                )

    except KeyError as err:
        log_err = f'ERROR - {remove_folder_data} -- {err}'
        logging.error(log_err)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
