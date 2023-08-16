'''Given a CSV list of assetIds, create a NetX Collection (group) via NetX API'''

import logging
import re
from datetime import datetime
from utils import netx_api as un
from utils import csv_tools as uc
from utils import setup

def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)

    config = setup.get_config_dams_netx(live_or_test)

    # Point the .env 'GROUP_ADD_CSV' variable at the CSV file with the list of assets 
    input_csv = config['GROUP_ADD_CSV']
    group_add_rows = uc.rows(input_csv)
    asset_id_list = [int(row['assetId']) for row in group_add_rows if len(re.findall(r'\D', row['assetId'])) == 0]

    collection_time = re.sub(r'\s|\:', '-', str(datetime.now())[:16])
    collection_title = f'API Collection {collection_time}'

    # Create new group
    collection_data = un.netx_create_collection(
        collection_title=collection_title,
        asset_id_list=asset_id_list,
        netx_env=live_or_test)
    
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

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
