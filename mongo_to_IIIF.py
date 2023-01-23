'''Return a IIIF manifest JSON file for an EMu irn in MongoDB'''

import json
import re
import sys
from pymongo import MongoClient
from utils import setup

def convert_emu_to_iiif(emu_record:dict, metadata_list:list, iiif_schema:dict) -> dict:
    '''format EMu multimedia record as iiif manifest'''

    iiif_manifest = iiif_schema

    emu_prep = {}

    for field in metadata_list:
        emu_prep[field] = emu_record[field]

    # TODO - Setup emu_prep as metadata

    # TODO - Check filetype & set corresponding manifest type

    # TODO generate json-output filename
    #   - replace "@id" values in json with values


    return iiif_manifest


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    emu_irn = sys.argv(1)

    if re.match(r'^\d+$', emu_irn) is None:
        raise Exception("Check first command-line argument -- expected numeric EMu irn, e.g. 34567")

    config = setup.get_config_dams_netx("LIVE")  # dotenv_values(".env")

    mongo_db = config['MONGO_DB']
    iiif_schema = json.load(config['IIIF_SCHEMA'])

    client = MongoClient(mongo_db)

    # get database
    db = client['emu']

    # get collection [table/module]
    emultimedia = db.emultimedia

    # get document [record]
    mm_document = emultimedia.find_one({"irn":emu_irn})
    # test_document = emultimedia.find_one({"irn":"2429133"})
    print(mm_document)

    if len(mm_document) < 1:
        raise Exception("Check input EMu IRN -- no matching irn found in MongoDB")

    # TODO - Add Dates, other time period/geo info
    field_list = ['MulTitle', 'MulDescription', 'AudCitation']

    iiif_manifest_json = convert_emu_to_iiif(
        emu_record=mm_document,
        metadata_list=field_list,
        iiif_schema=iiif_schema)

    iiif_manifest_json


    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
