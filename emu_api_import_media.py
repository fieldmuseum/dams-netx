'''Ingest media to sandbox env'''

import os
import re
import time
from datetime import datetime
from dotenv import dotenv_values
import utils.csv_tools as uc
import utils.emu_api as ue

def main(ingest_media:str=False):
    '''prep and import data and files from a prepped EMu import CSV'''

    config = dotenv_values('.env')

    rows = uc.rows(file = 'testing/emu_media_input/emultimedia.csv')

    # # Smaller test sample
    # rows = rows[32:]

    media_file_list = os.listdir('testing/emu_media_input')

    i = 0

    for record in rows:

        media_file = None

        time.sleep(3)

        i += 1
        if 'Multimedia' in record.keys():
            media_file = record['Multimedia']
            record.pop('Multimedia')
        
        if 'DetSubject_tab(1)' in record.keys():
            record['DetSubject_tab'] = [record['DetSubject_tab(1)']]
            if record['DetSubject_tab(2)'] is not None:
                record['DetSubject_tab'].append(record['DetSubject_tab(2)'])
            if record['DetSubject_tab(3)'] is not None:
                record['DetSubject_tab'].append(record['DetSubject_tab(3)'])
            
            # Drop bad colnames
            record.pop('DetSubject_tab(1)')
            record.pop('DetSubject_tab(2)')
            record.pop('DetSubject_tab(3)')

        if record['MulCreator_tab(1)'] is not None:
            record['MulCreator_tab'] = ['MulCreator_tab(1)']
            record.pop('MulCreator_tab(1)')

        # create new record
        new_mm = ue.emu_api_add_record('emultimedia', record, config['EMU_ENV'])
        new_irn = re.sub(r'(.+/)+', '', new_mm['id'])

        print(f"{i} : {new_irn} : {str(datetime.now())}")

        if ingest_media is True:

            time.sleep(3)

            # if corresponding media file exists, ingest it
            if media_file in media_file_list:
                media_file_path = 'testing/emu_media_input/'
                print(f'Importing file : {media_file_path}{media_file}')
                ue.emu_api_ingest_media_http(mm_irn=new_irn,
                                            media_path=media_file_path,
                                            media_name=media_file,
                                            emu_env=config['EMU_ENV'])

            else:
                print(f"warning -- media_file '{media_file}' not imported")


if __name__ == '__main__':
    main(ingest_media = False)
