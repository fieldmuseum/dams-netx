'''Transfer new updates from NetX directly to EMu via Texcdp'''

import logging
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from utils import csv_tools as uc
from utils import emu_api as ue
from utils import netx_api as un
from utils import emu_netx_map as emu_netx
from utils import setup
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
    netx_no_emu_irn = []
    prepped_emu_records = []
    netx_emu_map = emu_netx.get_dss_xml(config)

    for asset in netx_assets_to_update:

        print(asset)

        # 1 - Get corresponding EMu record

        if len(asset['attributes']['IRN']) > 0:
            emu_irn = asset['attributes']['IRN'][0]

            emu_record = ue.emu_api_query_numeric(
                emu_table="emultimedia",
                search_field="irn",
                search_value_single=emu_irn,
                emu_env=live_or_test
                )

            if 'matches' not in emu_record.keys():
                raise Exception("No matching EMu ")

        else:
            # TODO - if record is new / no EMu irn, import it to EMu
            # For now - log warning & output list of no-EMu-irn exceptions
            netx_no_emu_irn.append(asset)

            log_message_no_irn = f'Check NetX asset ID {asset["id"]} -- no EMu IRN in NetX record.'
            print(log_message_no_irn)
            logging.warning(log_message_no_irn)


        # 2 - Compare NetX / EMu fields
        # # Use netx/emu map (syncedMetadata.xml) to get corresponding EMu / NetX fields

        emu_updates_from_netx = {}

        for asset_field, asset_value in asset['attributes'].items():
        #   [# Map updated NetX-fields to EMu-fields]
            for emu_field, netx_field in netx_emu_map.items():
                if asset_field == netx_field:
                    # TODO - Transform asset_value structure for EMu data-types Ref, MVtable, etc
                    # if 'array' == ue.emu_api_check_field_type(emu_table, emu_field):
                    #     ...

                    # TODO - Only update fields with non-matching values
                    emu_updates_from_netx[emu_field] = asset_value

        # Update corresponding EMu records
        emu_update_log = ue.emu_api_update_record(
            emu_table="emultimedia",
            emu_irn=emu_irn,
            emu_record=emu_updates_from_netx,
            emu_env=live_or_test
            )

        logging.info(emu_update_log)

        prepped_emu_records.append(emu_updates_from_netx)

    # Output EMu-import CSV

    # get field names
    field_names = prepped_emu_records[0].keys()

    # setup output filepath + name
    output_path = config['LOG_OUTPUT']
    today = datetime.now()
    emu_csv_file = f'{output_path}emu_import_{today}.csv'

    if len(prepped_emu_records) > 0:
        uc.write_list_of_dict_to_csv(prepped_emu_records, field_names, emu_csv_file)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
