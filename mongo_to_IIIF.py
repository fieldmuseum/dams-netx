'''Return a IIIF manifest JSON file for an EMu irn in MongoDB'''

import logging
import json
import os
import re
import sys
from pymongo import MongoClient
from utils import setup
from utils import emu_netx_map


def get_iiif_schema(config:dict, emu_record:dict) -> dict:
    '''get the appropriate iiif manifest schema for a given file's type'''

    iiif_schema = json.load(open(config['IIIF_SCHEMA'], 'r', encoding='utf-8'))

    if re.findall(r'^http\://', emu_record['AudAccessURI']):
        iiif_file_id = re.sub(r'^http', 'https', emu_record['AudAccessURI'])
    else:
        iiif_file_id = emu_record['AudAccessURI']

    main_body = {
            "id": iiif_file_id,
            "type": None,
            "format": None
        }

    if emu_record['DetResourceSubtype'] == '3D Model':

        main_body['type'] = 'Model'

        # TODO - find correct iiif 'format' values for other 3D file-formats (OBJ, GLB)
        if re.findall(r'\.gltf$', emu_record['MulIdentifier']) is not None:
            main_body['format'] = 'model/gltf+json'
        elif re.findall(r'\.glb$', emu_record['MulIdentifier']) is not None:
            print('glb file')
            main_body['format'] = 'model/gltf-binary'
        elif re.findall(r'\.obj$', emu_record['MulIdentifier']) is not None:
            main_body['format'] = 'model/waveform+obj'
        else:
            iiif_format = re.sub(r'(.+)\..+$', '', emu_record['MulIdentifier'])
            main_body['format'] = f'model/{iiif_format}'

    elif emu_record['DetResourceType'] in ['Image', 'StillImage']:

        main_body['type'] = 'Image'

        iiif_format = re.sub(r'(.+)\..+$', '', emu_record['MulIdentifier'])
        main_body['format'] = f'image/{iiif_format}'

    # TODO - handle emu_record['DetResourceType'] in ['Sound', 'MovingImage]
    else:

        iiif_type = emu_record['DetResourceType']
        main_body['type'] = iiif_type

        iiif_format = re.sub(r'(.+)\..+$', '', emu_record['MulIdentifier'])
        main_body['format'] = f'{iiif_type.lower()}/{iiif_format}'

    iiif_schema['items'][0]['items'][0]['items'][0]['body'] = main_body


    return iiif_schema


def get_iiif_ids(
    iiif_manifest:dict,
    manifest_out_host,
    manifest_out_path,
    manifest_out_file
    ) -> dict:
    '''
    Populate iiif "id" fields with appropriate values for an asset.
    The HTTP domain-prefix for 'id' in the Canvas, Annotation & other objects
    needs to match the manifest's main 'id'
    '''

    iiif_manifest['id'] = f"{manifest_out_host}/{manifest_out_path}/{manifest_out_file}"

    # Add Canvas ID
    iiif_manifest['items'][0]['id'] = f"{manifest_out_host}/{manifest_out_path}/config/canvas"

    # Add AnnotationPage ID
    iiif_manifest['items'][0]['items'][0]['id'] = f"{manifest_out_host}/{manifest_out_path}/config/canvas/annotation_page"

    # Add AnnotationPage ID & target
    iiif_manifest['items'][0]['items'][0]['items'][0]['id'] = f"{manifest_out_host}/{manifest_out_path}/config/canvas/annotation_page/annotation"
    iiif_manifest['items'][0]['items'][0]['items'][0]['target'] = f"{manifest_out_host}/{manifest_out_path}/config/canvas"


    return iiif_manifest


def add_iiif_metadata(emu_record:dict, iiif_manifest:dict) -> dict:
    '''format EMu multimedia record as iiif manifest'''

    iiif_manifest['label']['en'] = [emu_record['MulTitle']]
    iiif_manifest['summary']['en'] = [emu_record['MulDescription']]
    iiif_manifest['requiredStatement']['value']['en'] = [emu_record['RightsSummaryDataLocal']]
    iiif_manifest['items'][0]['label']['en'] = [emu_record['MulTitle']]

    # Setup emu_prep as metadata
    field_list = emu_netx_map.emu_iiif_metadata_labels()

    metadata = []

    for field in field_list:
        if field in emu_record:
            emu_prep = {}
            emu_prep['label'] = {'en': [field_list[field]]}
            emu_prep['value'] = {'en': [emu_record[field]]}
            metadata.append(emu_prep)

    iiif_manifest['metadata'] = metadata

    return iiif_manifest

def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    emu_irn = sys.argv[1]

    if re.match(r'^\d+$', emu_irn) is None:
        raise Exception("Check first command-line argument -- expected numeric EMu irn, e.g. 34567")

    config = setup.get_config_dams_netx("LIVE")  # dotenv_values(".env")

    mongo_db = config['MONGO_DB']
    manifest_out_host = config['IIIF_OUT_HOST']
    manifest_out_path = f"{config['IIIF_OUT_PATH']}/{emu_irn}"
    manifest_out_file = config['IIIF_OUT_FILE']

    client = MongoClient(mongo_db)

    # get database
    db = client['emu']

    # get collection [table/module]
    emultimedia = db.emultimedia

    try:
        # get document [record]
        mm_document = emultimedia.find_one({"irn":emu_irn})
        # test_document = emultimedia.find_one({"irn":"2429133"})
        print(mm_document)

        # if mm_document is None:
        #     raise Exception("Check input EMu IRN -- no matching irn found in MongoDB")

        # Setup manifest with schema appropriate for media-type
        iiif_schema = get_iiif_schema(config, mm_document)

        # Add ID's to manifest
        iiif_manifest = get_iiif_ids(
            iiif_schema,
            manifest_out_host,
            manifest_out_path,
            manifest_out_file
            )

        # Add title, description & info from EMu record
        iiif_manifest_json = add_iiif_metadata(
            emu_record=mm_document,
            iiif_manifest=iiif_manifest
            )


        # If better to write output to console:
        print(iiif_manifest_json)


        # Check if output path exists
        if not os.path.exists(manifest_out_path):
            os.makedirs(manifest_out_path)
            
        f = open(f'{manifest_out_path}/{manifest_out_file}', 'w', encoding='utf-8')
        f.write(json.dumps(iiif_manifest_json, indent=True, ensure_ascii=False))
        f.close()


    except TypeError as err_type:
        log_err = f'ERROR - Check input EMu IRN; no matching irn found for {emu_irn} in MongoDB. TypeError: {err_type}'
        print(log_err)
        logging.error(log_err)
        return err_type


    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
