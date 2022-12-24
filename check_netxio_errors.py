'''Check NetXIO lostandfound and sync.log errors'''

import hashlib
import logging
import os
import re
import shutil
# from fileinput import filename
from utils import setup
from utils import netx_api


def list_files(directory:str):
    '''get a list of files with full filepaths in a directory (recursive)'''

    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_name = file
            file_path = os.path.join(root, file)
            file_row = {
                'name':file_name,
                'path':file_path
            }
            paths.append(file_row)

    return paths


def main():
    '''Main function'''

    setup.start_log_dams_netx()

    live_or_test = setup.get_sys_argv()

    config = setup.get_config_dams_netx(live_or_test)

    if live_or_test == 'LIVE':
        netxio_source_dir = config['NETXIO_LOCAL_SOURCE_DIR']
        netxio_lost_dir = config['NETXIO_LOSTANDFOUND']

    else:
        netxio_source_dir = config['TEST_NETXIO_LOCAL_SOURCE_DIR']
        netxio_lost_dir = config['TEST_NETXIO_LOSTANDFOUND']

    lost_and_found_files = list_files(netxio_lost_dir)

    # check for trailing slash in NetXIO source dir value
    if re.match(r'.*/$', netxio_source_dir) is None:
        netxio_source_dir += '/'


    # Check each lost-&-found file
    for file_row in lost_and_found_files:

        file_name = file_row['name']
        file_path = file_row['path']

        # - by checksum
        # - - get md5 of lost-found-file
        with open(file_path,'rb') as media_file:
            file_bytes = media_file.read()
            file_md5 = hashlib.md5(file_bytes).hexdigest()

        asset_data_md5 = netx_api.netx_get_asset_by_field(
            search_field="fileChecksum",
            search_value=file_md5,
            netx_test=live_or_test
            )

        # Get NetX Asset ID by md5
        # If found, remove
        if 'result' in asset_data_md5 and len(asset_data_md5['result']['results']) > 0:

            asset_id = f"NetX asset {asset_data_md5['result']['results'][0]['id']}"

            log_msg = f'Removed {file_name} from lostandfound: md5 {file_md5} matches {asset_id}'
            print(log_msg)
            logging.info(log_msg)

            os.remove(file_path)

        # If not found, check by filename (next if/else)
        else:

            # Check if file is in NetX
            # - by filename
            asset_data = netx_api.netx_get_asset_by_filename(
                file_name=file_name,
                netx_env=live_or_test
                )

            if 'result' in asset_data and len(asset_data['result']['results']) > 0:

                asset_id = f"NetX asset {asset_data['result']['results'][0]['id']}"
                os.remove(file_path)

                log_message = f'Removed {file_name} from lostandfound - guid matches {asset_id}'
                print(log_message)
                logging.info(log_message)


            elif 'result' in asset_data and len(asset_data['result']['results']) < 1:

                file_path_edit = re.sub(netxio_lost_dir ,'', file_path)
                file_path_edit = re.sub(file_name ,'', file_path_edit)
                moving_file = f'file for NetXIO returned to: {netxio_source_dir + file_path_edit}'

                log_message = f'No NetX match for {file_name} (md5 {file_md5}) - {moving_file}'
                print(log_message)
                logging.info(log_message)


                if os.path.exists(netxio_source_dir + file_path_edit) is False:
                    os.makedirs(netxio_source_dir + file_path_edit)

                if os.path.exists(netxio_source_dir + file_path_edit + file_name) is False:
                    shutil.move(file_path, netxio_source_dir + file_path_edit)

            else:

                log_message = 'Possible API error'
                print(log_message)
                logging.error(log_message)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
