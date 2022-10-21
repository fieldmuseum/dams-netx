'''Output a CSV of assets recently updated in NetX (via the NetX API)'''

from datetime import datetime, timedelta
# import logging, time
import utils.netx_api as un
import utils.csv_tools as uc
import utils.setup as setup
# from dotenv import dotenv_values

def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)

    config = setup.get_config_dams_netx(live_or_test)  # dotenv_values(".env")

    # Get assets updated since last check/export
    start_date = datetime.now() - timedelta(days = +2, hours = 0)

    netx_assets = un.netx_get_asset_by_range(
        search_field = "modDate",
        search_min = str(start_date),
        data_to_get = ['asset.id', 'asset.attributes'],
        netx_test = live_or_test
        )
    
    netx_assets_to_update = []

    if netx_assets['result'] is not None:
        if len(netx_assets['result']['results']) > 0:
            netx_assets_to_update = netx_assets['result']['results']
    
    print(netx_assets)


    # Reformat each asset as an EMu-import CSV row [for now]
    prepped_emu_records = []

    for asset in netx_assets_to_update:

        print(asset)
        
        emu_record = {}
        
        # # TODO: use syncedMetadata.xml map (or other schema) to get each EMu field for corresponding NetX attribute
        if len(asset['attributes']['IRN']) > 0:
            emu_record['irn'] = asset['attributes']['IRN'][0]
        
        if len(asset['attributes']['Title']) > 0:
            emu_record['MulTitle'] = asset['attributes']['Title'][0]
        
        if len(asset['attributes']['Description']) > 0:
            emu_record['MulDescription'] = asset['attributes']['Description'][0]

        prepped_emu_records.append(emu_record)

    # Output EMu-import CSV

    print(prepped_emu_records)
    
    # get field names
    field_names = prepped_emu_records[0].keys()

    # setup output filepath + name
    output_path = config['LOG_OUTPUT']
    today = datetime.now()
    emu_csv_file = f'{output_path}emu_import_.csv'


    if len(prepped_emu_records) > 0:
        uc.write_list_of_dict_to_csv(prepped_emu_records, field_names, emu_csv_file)

    # # Get id's for unique list of folders may be quicker
    # folder_id_list = get_unique_folder_id_list(path_add_rows, live_or_test)

    # # Add assets to folders
    # for row in path_add_rows:
    #     add_to_folder(row, folder_id_list, live_or_test)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
  main()
