'''Transfer new updates from EMu (via Texcdp) directly to NetX'''

import logging, re
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import utils.csv_tools as uc
import utils.emu_api as ue
import utils.netx_api as un
import utils.emu_netx_map as emu_netx
import utils.setup as setup
# from dotenv import dotenv_values


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)

    config = setup.get_config_dams_netx(live_or_test)  # dotenv_values(".env")

    # Get assets updated since last check/export
    start_date = datetime.now() - timedelta(days = +2, hours = 0)
    start_date = re.sub(r'\s+.*', '', str(start_date))
    end_date = re.sub(r'\s+.*', '', str(datetime.now()))

    emu_records = ue.emu_api_query_text(
        emu_table = 'emultimedia',
        search_field = 'AdmDateModified',
        operator = 'range',
        search_value_range = [start_date,end_date],
        emu_env = live_or_test
        )

    # netx_assets = un.netx_get_asset_by_range(
    #     search_field = "modDate",
    #     search_min = str(start_date),
    #     data_to_get = ['asset.id', 'asset.attributes'],
    #     netx_test = live_or_test
    #     )
    
    records_to_update = []

    if 'matches' in emu_records.keys():
        if len(emu_records['matches']) > 0:
            records_to_update = emu_records['matches']
    
    # print(netx_assets)


    # Reformat each asset as an EMu-import CSV row [for now]
    prepped_netx_records = []
    netx_emu_map = emu_netx.get_dss_xml(config)

    # TODO - list of NetX fields to retrieve to cross-check w/ updated EMu record
    data_to_get = ['asset.base']

    for record in records_to_update:

        # print(record)

        # 1 - Get corresponding NetX record
        
        emu_irn = re.sub(r'(.*/)+', '', record['id'])

        netx_record = un.netx_get_asset_by_field(
            search_field = 'EMu IRN',
            search_value = emu_irn,
            data_to_get = data_to_get,
            netx_test = live_or_test
            )

        if 'result' not in netx_record.keys() :
            raise Exception("Check NetX API & Config - No results")
        elif 'results' not in netx_record['result'].keys() or len(netx_record['result']['results']) < 1:
            raise Exception(f"Check EMu irn {emu_irn} - No matching NetX record")
        
        netx_asset_id = netx_record['result']['results'][0]['asset.id']

        # 2 - Compare NetX / EMu fields
        # # Use netx/emu map (syncedMetadata.xml) to get corresponding EMu / NetX fields

        netx_updates_from_emu = {}

        for emu_field, emu_value in record['attributes'].items():
        #   [# Map updated NetX-fields to EMu-fields]
            for emu_field, netx_field in netx_emu_map.items():
                if emu_field == netx_field:

                    # TODO - Transform emu_value structure for NetX data-types (Ref, MV-tables, etc)
                    # if 'array' == ue.emu_api_check_field_type(emu_table, emu_field):
                    #     ...

                    # TODO - get media-file from EMu, rename + ingest to NetX
                    
                    # TODO - Only update fields with non-matching values

                    netx_updates_from_emu[emu_field] = emu_value        

        # Update corresponding NetX records
        netx_update_log = un.netx_update_asset(
            asset_id = netx_asset_id,
            data_to_update = netx_updates_from_emu,
            data_to_get = ['asset.base'],
            netx_env = live_or_test
            )
        
        logging.info(netx_update_log)

        prepped_netx_records.append(netx_updates_from_emu)

    # Output EMu-import CSV
    
    # get field names
    field_names = prepped_netx_records[0].keys()

    # setup output filepath + name
    output_path = config['LOG_OUTPUT']
    today = datetime.now()
    netx_csv_file = f'{output_path}netx_import_{today}.csv'

    if len(prepped_netx_records) > 0:
        uc.write_list_of_dict_to_csv(prepped_netx_records, field_names, netx_csv_file)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()

