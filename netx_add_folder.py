'''Add ingested assets to secondary folders via NetX API'''

import logging
import time
from utils import netx_api as un
from utils import csv_tools as uc
from utils import setup
# from dotenv import dotenv_values


def add_to_folder(row:dict, folder_id_list:dict, live_or_test:str):
    '''For a given asset's filename and pathAdd folder-name, add the asset to the folder'''

    # In case API needs rate-limiting
    time.sleep(0.1)

    # Given Identifier/Filename, Get Asset ID
    asset_data = un.netx_get_asset_by_filename(
        row['file'],
        data_to_get=['asset.id','asset.folders'],
        netx_env=live_or_test
        )

    if 'result' not in asset_data or len(asset_data['result']['results']) < 1:
        logging.error(asset_data)
        return

    asset_id = asset_data['result']['results'][0]['id']
    asset_folders = asset_data['result']['results'][0]['folders']
    asset_orig_folder_ids = [folder['id'] for folder in asset_folders]

    # Get Asset's Secondary Department-folders
    folder_name = row['pathAdd']
    if folder_name in folder_id_list.keys():
        folder_id = folder_id_list[folder_name]

        if folder_id in asset_orig_folder_ids:
            log_message = f'Asset {asset_id} already in folder {folder_id}; Skipping'
            print(log_message)
            logging.info(log_message)
            return

    else:
        log_error = f'Missing Folder {folder_name}'
        logging.error(log_error)
        return


    # Add Asset to Folder/s -- https://developer.netx.net/#addassettofolder
    folder_data = un.netx_add_asset_to_folder(asset_id, folder_id, netx_env=live_or_test)

    if 'result' in folder_data:
        folders = [folder['path'] for folder in folder_data['result']['folders']]
        asset = folder_data['result']['file']['name']
        log_message = f'{asset} - folders updated to: {folders}'
        print(log_message)
        # row['status'] = folder_data['result']
        logging.info(log_message)

    else:
        print(f'ERROR - {folder_data}')
        # row['status'] = folder_data
        logging.error(folder_data)

    return


def get_unique_folder_id_list(path_add_rows:list, live_or_test:str):
    '''
    Given a pathAdd CSV, retrieve folder IDs for a unique list of folder-names
    Return a list of {folder_name:folder_id}
    '''

    unique_folders = []

    for row in path_add_rows:

        if row['pathAdd'] not in unique_folders:
            unique_folders.append(row['pathAdd'])

    folder_id_list = {}

    if len(unique_folders) > 0:
        for folder_name in unique_folders:

            # Get Asset's Secondary Departments
            folder_data = un.netx_get_folder_by_path(
                folder_path=folder_name,
                data_to_get=None,
                netx_env=live_or_test
                )

            try:
                folder_id = folder_data['result']['id']
                folder_id_list[folder_name] = folder_id

            except KeyError as err:
                err_message = f'ERROR - {folder_data}: {err}'
                print(err_message)
                logging.error(err_message)

    return folder_id_list


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)
    # live_or_test = sys.argv[1]

    config = setup.get_config_dams_netx(live_or_test)  # dotenv_values(".env")

    input_csv = config['PATHADD_CSV']
    path_add_rows = uc.rows(input_csv)

    # Get id's for unique list of folders may be quicker
    folder_id_list = get_unique_folder_id_list(path_add_rows, live_or_test)

    # Add assets to folders
    for row in path_add_rows:
        add_to_folder(row, folder_id_list, live_or_test)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
