'''Given a CSV list of assetIds, create a NetX Collection (group) via NetX API'''

import logging
import math
import time
import re
import sys
from datetime import datetime
from utils import netx_api as un
from utils import csv_tools as uc
from utils import setup

def main(live_or_test:str=None):
    '''main function'''

    # Setup paths to input XML
    if live_or_test is None:
        input_args = sys.argv
        live_or_test = setup.get_sys_argv(1)

    else:
        input_args = [live_or_test]

    setup.start_log_dams_netx(config=None, cmd_args=input_args)

    config = setup.get_config_dams_netx(live_or_test)

    # Point the .env 'GROUP_ADD_CSV' variable at the CSV file with the list of assets
    input_csv = config['GROUP_ADD_CSV']
    group_add_rows = uc.rows(input_csv)
    asset_id_list = [int(row['assetId']) for row in group_add_rows if len(re.findall(r'\D', row['assetId'])) == 0]

    # Break down list into chunks if > 3000 assets
    # if len(asset_id_list) > 3000:
    asset_list_list = []
    chunk_size = 15000
    start_chunk = 1
    chunks = math.ceil(len(asset_id_list)/chunk_size)

    for i in list(range(start_chunk,chunks)):
        chunk_min = chunk_size*(i-1)
        chunk_max = chunk_size*i
        asset_list_list.append(asset_id_list[chunk_min:chunk_max])
        i += 1

    collection_time = re.sub(r'\s|\:', '-', str(datetime.now())[:16])
    collection_title = f'API Collection {collection_time}'

    # Create new groups
    chunk_number = start_chunk
    for asset_list_chunk in asset_list_list:
        collection_data = un.netx_create_collection(
            collection_title=f'{collection_title}_{chunk_number}',
            asset_id_list=asset_list_chunk,  # asset_id_list,
            netx_env=live_or_test)

        chunk_number += 1


        if 'result' in collection_data:
            col_id = collection_data['result']['id']
            col_title = collection_data['result']['title']
            col_item_count = collection_data['result']['itemCount']
            log_message = f'{col_title} - id {col_id} - created collection of {col_item_count} assets'
            print(log_message)
            logging.info(log_message)

        else:
            print(f'ERROR - {collection_data}')
            logging.error(collection_data)

        time.sleep(10)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
