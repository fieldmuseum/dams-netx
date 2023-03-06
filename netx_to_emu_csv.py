'''Transfer new updates from NetX XML export to EMu CSV import'''

from datetime import datetime
from utils import csv_tools as uc
from utils import xml_tools as ux
from utils import emu_netx_map as emu_netx
from utils import setup


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)

    config = setup.get_config_dams_netx(live_or_test)  # , datetime.now())  # dotenv_values(".env")

    # TODO - Copy NetX export XML from DAMS-HOST to local:
    # dams_host = config['DAMS_HOST_2']
    # dams_id = config['DAMS_HOST_2_ID'] 
    # dams_pw = config['DAMS_HOST_2_PW']
    netx_xml = config['NETX_XML_EXPORT']

    
    # Read in NetX XML
    xml_date = datetime.strftime(datetime.now(), '%Y-%-m-%-d')
    netx_assets_to_update = ux.get_input_xml(netx_xml, xml_date)


    # Reformat each asset as an EMu-import CSV row [for now]
    netx_no_emu_irn = []
    prepped_emu_records = []
    # netx_emu_map = emu_netx.get_dss_xml(config)

    for asset_raw in netx_assets_to_update:

        # TODO - refactor / setup function for loop below
        # emu_prepped = convert_netx_to_emu(asset_raw)

        asset = asset_raw[0]

        emu_prepped = {}
        print(str(asset.tag))

        for asset_attrib in asset:
            print(asset_attrib.tag)
            emu_prepped[str(asset_attrib.tag)] = str(asset_attrib.text)

            print(f'{asset_attrib.tag} = {asset_attrib.text}')
            print(emu_prepped)

            if asset_attrib.tag == "DetSubjects" and asset_attrib.text is not None:
                asset_subjects = asset_attrib.text.split(',')

                for subject in asset_subjects:
                    subject_row = f'DetSubject_tab({asset_subjects.index(subject) + 1})'
                    emu_prepped[subject_row] = subject
                
                emu_prepped.pop('DetSubjects')

        # 1 - Handle NetX asset without corresponding EMu MM separately
        if emu_prepped['MulOtherNumber'] is None:
            netx_no_emu_irn.append(emu_prepped)
        
        else:
            emu_irn = {'irn': emu_prepped['MulOtherNumber']}
            emu_prepped.pop('MulOtherNumber')

            print(f'emu_irn type = {type(emu_irn)}')
            print(f'emu_prepped type = {type(emu_prepped)}')

            emu_prepped_ordered = emu_irn | emu_prepped  # {**emu_irn, **emu_prepped}  # 
            prepped_emu_records.append(emu_prepped_ordered)

            print(emu_prepped_ordered)

        # 2 - Compare NetX / EMu fields
        # # Use netx/emu map (syncedMetadata.xml) to get corresponding EMu / NetX fields


    # Output EMu-import CSV

    # get field names
    if len(prepped_emu_records) > 0:
        field_names = prepped_emu_records[0].keys()

        # setup output filepath + name
        output_path = config['LOG_OUTPUT']
        emu_csv_file = f'{output_path}emu_import_{xml_date}.csv'

        if len(prepped_emu_records) > 0:
            uc.write_list_of_dict_to_csv(prepped_emu_records, field_names, emu_csv_file)

    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
