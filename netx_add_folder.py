'''Add ingested assets to secondary folders via NetX API'''

from datetime import date
import utils.netx_api as un
import utils.csv_tools as uc
from dotenv import dotenv_values


def add_to_folder(row:dict):
    '''For a given asset's filename and pathAdd folder-name, add the asset to the folder'''

    # Given Identifier/Filename, Get Asset ID 
    asset_data = un.netx_get_asset_by_filename(row['filename'])
    asset_id = asset_data['result']['results'][0]['id']

    # Get Asset's Secondary Departments
    folder_data = un.netx_get_folder_by_path("column 2 from input CSV")
    folder_id = folder_data['result']['id']

    # Add Asset to Folder/s -- https://developer.netx.net/#addassettofolder
    log = un.netx_add_asset_to_folder(asset_id, folder_id)

    row['status'] = log['result']


def main():
    '''main function'''

    config = dotenv_values(".env")
    input_csv = config['PATHADD_CSV_FILE']
    path_add_rows = uc.rows(input_csv)

    # NOTE - first getting id's for unique list of folders may be quicker

    logs = []

    for row in path_add_rows:
        log_row = add_to_folder(row)
        logs.append(log_row)

    field_names = logs[0].keys()

    output_file = config['LOG_OUTPUT'] + 'netx_add_folder_log_' + date.today() + '.csv'
    uc.write_list_of_dict_to_csv(logs, field_names, output_file)


if __name__ == '__main__':
  main()
