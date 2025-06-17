'''Ingest media to sandbox env'''

import re
import time
from datetime import datetime
from dotenv import dotenv_values
import utils.csv_tools as uc
import utils.emu_api as ue

def main():
    '''prep and import data and files from a prepped EMu import CSV'''

    config = dotenv_values('.env')

    # TODO - Update from hardcoded path for prod
    rows = uc.rows(file = 'testing/emu_media_input/emultimedia.csv')

    # Smaller test sample
    rows = rows[24:]

    i = 0

    for record in rows:

        irn = record['irn']
        prepped_record = {}

        # Manually patching Subject/Keywords
        prepped_record['DetSubject_tab'] = []

        if 'DetSubject_tab(1)' in record.keys():
            prepped_record['DetSubject_tab'].append(record['DetSubject_tab(1)'])
        if record['DetSubject_tab(2)'] is not None:
            prepped_record['DetSubject_tab'].append(record['DetSubject_tab(2)'])
        if record['DetSubject_tab(3)'] is not None:
            prepped_record['DetSubject_tab'].append(record['DetSubject_tab(3)'])
        if record['DetSubject_tab(4)'] is not None:
            prepped_record['DetSubject_tab'].append(record['DetSubject_tab(4)'])

        # prepped_record['DetResourceType'] = record['DetResourceType']
        # prepped_record['DetSubject_tab'] = [record['DetSubject_tab']]
        # prepped_record['SecRecordStatus'] = record['SecRecordStatus']

        time.sleep(2)

        i += 1

        # check for existing record
        mm_record = ue.emu_api_get_record_by_irn(emu_table='emultimedia',
                                                 search_field='irn', 
                                                 operator='exact',
                                                 search_value_single=irn,
                                                 emu_env=config['EMU_ENV'])

        if mm_record['hits'] == 1:
            # match_record = mm_record['matches'][0]['data']

            ue.emu_api_update_record(emu_table='emultimedia',
                                     emu_irn=irn, 
                                     operation='replace',
                                     emu_record=prepped_record,
                                     emu_env=config['EMU_ENV'])

            print(f"{i} : Updated record {irn} : {str(datetime.now())}")


        else:
            # If no match, create new record
            new_mm = ue.emu_api_add_record('emultimedia', record, config['EMU_ENV'])
            new_irn = re.sub(r'(.+/)+', '', new_mm['id'])

            print(f"{i} : New record {new_irn} : {str(datetime.now())}")


if __name__ == '__main__':
    main()
