'''Remove assets via NetX API if they were unpublished/deleted in EMu'''

import logging, time
import utils.netx_api as un
import utils.csv_tools as uc
import utils.setup as setup
# from dotenv import dotenv_values


def remove_from_netx(row:dict, folder_id_list:dict, live_or_test:str):
    '''For a given asset's filename, pathMove asset to the 'Remove From NetX' folder [remove from all other folders]'''

    # In case API needs rate-limiting
    time.sleep(0.1)

    # Given Identifier/Filename, Get Asset ID 
    asset_data = un.netx_get_asset_by_filename(row['file'], data_to_get=['asset.id','asset.folders'], netx_env=live_or_test)

    # print(f'asset_data = {asset_data}')

    if 'result' not in asset_data or len(asset_data['result']['results']) < 1:
        logging.error(asset_data)
        return

    else:
        asset_id = asset_data['result']['results'][0]['id']
        asset_orig_folder_ids = [folder['id'] for folder in asset_data['result']['results'][0]['folders']]

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
        logging.error(f'Missing Folder {folder_name}')
        return

    
    # TODO - Remove asset from all but 'Remove from NetX' folder
    remove_asset_log = un.netx_remove_asset_from_folder(asset_id=asset_id, folder_id = folder_id, netx_env=live_or_test)


    # # Add Asset to 'Remove from NetX' Folder -- https://developer.netx.net/#addassettofolder
    folder_id = folder_id_list['Remove from NetX']
    folder_data = un.netx_add_asset_to_folder(asset_id, folder_id, netx_env=live_or_test)

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
            folder_data = un.netx_get_folder_by_path(folder_path=folder_name, data_to_get=None, netx_env=live_or_test)

            if 'result' not in folder_data:
                print(f'ERROR - {folder_data}')
                logging.error(folder_data)
                return

            else:
                folder_id = folder_data['result']['id']
                folder_id_list[folder_name] = folder_id

    return folder_id_list


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)
    # live_or_test = sys.argv[1]

    config = setup.get_config_dams_netx(live_or_test)  # dotenv_values(".env")

    input_csv = config['PATHADD_CSV_FILE']
    path_add_rows = uc.rows(input_csv)

    # Get id's for unique list of folders may be quicker
    folder_id_list = get_unique_folder_id_list(path_add_rows, live_or_test)

    # Add assets to folders
    for row in path_add_rows:
        remove_from_netx(row, folder_id_list, live_or_test)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
  main()
