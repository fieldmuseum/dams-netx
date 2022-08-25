'''Check NetXIO lostandfound and sync.log errors'''

import os, hashlib, logging
import utils.setup as setup
import utils.netx_api as netx_api


def main():
    '''Main function'''

    setup.start_log_dams_netx()

    config = setup.get_config_dams_netx()
    lost_and_found_files = os.listdir(config['NETXIO_LOSTANDFOUND'])  # os.walk()

    for file_name in lost_and_found_files:

        # Check if file is in NetX
        # - by filename
        asset_data = netx_api.netx_get_asset_by_filename(file_name)

        if 'result' in asset_data:

            if len(asset_data['result']['results']) > 0:

                asset_id = asset_data['result']['results'][0]['id']

                log_message= f'{file_name} is NetX asset {asset_id}'
                print(log_message)
                logging.info(log_message)


            else:
                
                # - by checksum
                # - - get md5 of lost-found-file
                file_md5 = hashlib.md5(open(file_name, 'rb')).hexdigest()
                asset_data = netx_api.netx_get_asset_by_field("fileChecksum", file_name)

                # Get NetX Asset ID by md5
                if 'result' in asset_data:

                    if len(asset_data['result']['results']) < 1:

                        print(f'no NetX match for {file_name}')
                        logging.error(asset_data)

                        # IMPORT FILE / preserve folder path
                    
                    else:

                        asset_id = asset_data['result']['results'][0]['id']

                        log_message= f'{file_name} (md5 = {file_md5}) is NetX asset {asset_id}'
                        print(log_message)
                        logging.info(log_message)
                        

        

        # - - getAsset by md5

    setup.stop_log_dams_netx()


if __name__ == '__main__':
  main()
