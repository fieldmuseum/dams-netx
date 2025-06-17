'''Retrieve Multimedia records from sandbox env'''

import json
import os
import time
from datetime import datetime
from dotenv import dotenv_values
import utils.emu_api as ue
import utils.csv_tools as uc

def main():
    '''prep and import data and files from a prepped EMu import CSV'''

    config = dotenv_values('.env')

    # rows = uc.rows(file = 'testing/emu_media_input/emultimedia.csv')
    mm_irns = range(110,153)

    # # Smaller test sample
    # mm_irns = range(115,125)

    mm_output_list = []

    i = 0

    for irn in mm_irns:

        time.sleep(3)

        i += 1

        # find record
        record_raw = ue.emu_api_get_record_by_irn(emu_table='emultimedia',
                                                  search_field='irn',
                                                  operator='exact',
                                                  search_value_single=irn,
                                                  emu_env=config['EMU_ENV'])

        print(f"{i} : irn {irn}  :  {str(datetime.now())}")

        record = record_raw['matches'][0]['data']

        mm_output_list.append(record)

        time.sleep(6)

    if len(mm_output_list) > 0:

        out_path = 'testing/emu_data_output'
        out_json = f'record_list_{datetime.now()}.json'
        out_csv = f'record_list_{datetime.now()}.csv'

        # Check if output path exists
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        f = open(f'{out_path}/{out_json}', 'w', encoding='utf-8')
        f.write(json.dumps(mm_output_list, indent=4, ensure_ascii=False))
        f.close()

        uc.write_list_of_dict_to_csv(input_records=mm_output_list,
                                     field_names=mm_output_list[0].keys(),
                                     output_csv_file_name=f'{out_path}/{out_csv}')


if __name__ == '__main__':
    main()
