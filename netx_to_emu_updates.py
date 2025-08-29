'''Transfer new updates from NetX directly to EMu via emurestapi'''

import logging
import re
from datetime import datetime, timedelta
import utils.csv_tools as uc
import utils.emu_api as ue
import utils.netx_api as un
import utils.emu_netx_map as emu_netx
import utils.setup as setup
# from dotenv import dotenv_values

def get_corresponding_emu_record(asset, live_or_test):
    '''find EMu MM record based on NetX IRN-attribute'''

    emu_guid = asset['name']

    # if len(asset['attributes']['IRN']) > 0:

        # emu_record = ue.emu_api_query_numeric(
        #     emu_table="emultimedia",
        #     search_field="irn",
        #     search_value_single=emu_irn,
        #     emu_env=live_or_test
        #     )

    emu_record = ue.emu_api_query_text(
        emu_table="emultimedia",
        search_field="AdmGUIDPreferredValue",
        search_value_single=emu_guid,
        emu_env=live_or_test
        )

    if 'matches' not in emu_record.keys():

        # - ALSO CHECK FOR MATCHING MD5SUM? (in MAIN or SUPP)
        netx_md5 = asset['file']['checksum']

        emu_record = ue.emu_api_query_text(
            emu_table="emultimedia",
            search_field="ChaMd5Sum",
            search_value_single=netx_md5,
            emu_env=live_or_test
            )

        if 'matches' not in emu_record.keys():

            emu_record = ue.emu_api_query_text(
                emu_table="emultimedia",
                search_field="SupMd5Checksum",
                search_value_single=netx_md5,
                emu_env=live_or_test
                )

            if 'matches' not in emu_record.keys():

                raise Exception("No matching EMu record")

    return emu_record


def update_corresponding_emu_record(asset, field_map, live_or_test):
    '''Update existing EMu record [when a match IS found]'''

    # Map netx_asset values to emu_record values
    attributes_to_emu = asset['attributes']
    asset_to_emu = {}
    for attribute in attributes_to_emu:
        emu_column = field_map[attribute]
        asset_to_emu[emu_column] = asset['attribute'][attribute]

    # Update EMu record
    emu_record = ue.emu_api_add_record(
        emu_table="emultimedia",
        new_emu_record=asset_to_emu,
        emu_env=live_or_test
        )

    return emu_record


def create_corresponding_emu_record(asset, field_map, live_or_test):
    '''insert new EMu record [when NO match is found]'''

    # Map netx_asset values to emu_record values
    asset_to_emu = ''

    # Create EMu record
    emu_record = ue.emu_api_add_record(
        emu_table="emultimedia",
        new_emu_record=asset_to_emu,
        emu_env=live_or_test
        )

    return emu_record


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)

    config = setup.get_config_dams_netx(live_or_test)  # dotenv_values(".env")

    # Get EMu/NetX mapping
    field_map = emu_netx.get_emu_netx_map(config)

    # Get assets updated since last check/export
    start_date = datetime.now() - timedelta(days = +2, hours = 0)

    netx_assets = un.netx_get_asset_by_range(
        search_field = "modDate",
        search_min = str(start_date),
        data_to_get = ['asset.id', 'asset.attributes', 'asset.file'],
        netx_test = live_or_test
        )

    netx_assets_to_update = []

    if netx_assets['result'] is not None:
        if len(netx_assets['result']['results']) > 0:
            netx_assets_to_update = netx_assets['result']['results']

    print(netx_assets)

    # NOTE:
    # SEPARATE scripts/functions/process for:
    #  1 - Old record updates
    #        -
    #  2 - New record inserts
    #  3 - Deletes?

    # Reformat each asset as an EMu-import CSV row [for now]
    netx_no_emu_match = []
    prepped_emu_records = []
    netx_emu_map = emu_netx.get_dss_xml(config)

    for asset in netx_assets_to_update:

        print(asset)

        # 1 - Check/Get corresponding EMu record

        # if len(asset['attributes']['IRN']) > 0:
        # emu_irn = asset['attributes']['IRN'][0]

        emu_record = get_corresponding_emu_record(asset,
                                                  live_or_test)

        if emu_record is None or len(emu_record['results']) == 0:

            emu_record = create_corresponding_emu_record(asset,
                                                         field_map,
                                                         live_or_test)

            # Update list & log of newly created EMu records
            netx_no_emu_match.append(asset)

            log_message_no_irn = f'Check NetX asset ID {asset["id"]} -- no EMu IRN in NetX record.'
            print(log_message_no_irn)
            logging.warning(log_message_no_irn)

        else:
            # If record exists, update it
            emu_record = update_corresponding_emu_record(asset,
                                                         field_map,
                                                         live_or_test)

            # Update corresponding EMu records
            # TODO - GET PROPER PATH TO IRN
            emu_irn = re.sub(r'(.+/)*', '', emu_record['id'])

            emu_update_log = ue.emu_api_update_record(
                emu_table="emultimedia",
                emu_irn=emu_irn,
                emu_record=emu_updates_from_netx,
                emu_env=live_or_test
                )

            logging.info(emu_update_log)
            prepped_emu_records.append(emu_updates_from_netx)


        # 2 - Compare NetX / EMu fields
        # # Use netx/emu map (syncedMetadata.xml) to get corresponding EMu / NetX fields

        emu_updates_from_netx = {}

        for asset_field, asset_value in asset['attributes'].items():
            # [# Map updated NetX-fields to EMu-fields]
            for emu_field, netx_field in netx_emu_map.items():
                if asset_field == netx_field:
                    # TODO - Transform asset_value structure for EMu data-types Ref, MVtable, etc
                    # if 'array' == ue.emu_api_check_field_type(emu_table, emu_field):
                    #     ...

                    # TODO - Only update fields with non-matching values
                    emu_updates_from_netx[emu_field] = asset_value

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
