"""
Rename files and copy them to NetX Multimedia folder-structure

CSV parsing and writing:
https://realpython.com/python-csv/
"""

import csv
import glob
import logging
import os
import re
import sys
# from decouple import config
import xml.etree.ElementTree as ET
from exiftool import ExifToolHelper, exceptions
from fabric import Connection
from utils import emu_netx_map as emu_netx
from utils import setup


def main():
    """
    Outputs all records' data and copies files into dir for NetX
    Input is an EMu XML export file, outputs to a CSV file with the
    filename (identifier + file-extension) and filepath (prep_file).

    :param file_path: filename of the XML file to parse
    :return: list of dictionaries, dictionary includes: AudIdentifier, prep_file
    """
    # Main function

    # Start logs
    setup.start_log_dams_netx(config=None, cmd_args=sys.argv)
    # input_date = sys.argv[1]
    # live_or_test = sys.argv[2]
    live_or_test, input_date = setup.get_sys_argv()

    config = setup.get_config_dams_netx(live_or_test)

    dept_csv = config['DEPARTMENT_CSV']

    # Check if test or live paths should be used
    full_prefix = setup.get_path_from_env(
        live_or_test,
        config['ORIGIN_PATH_MEDIA'],
        config['TEST_ORIGIN_PATH_MEDIA']
        )
    full_xml_prefix = setup.get_path_from_env(
        live_or_test,
        config['ORIGIN_PATH_XML'],
        config['TEST_ORIGIN_PATH_XML']
        )
    dest_prefix = setup.get_path_from_env(
        live_or_test,
        config['DESTIN_PATH_MEDIA'],
        config['TEST_DESTIN_PATH_MEDIA']
        )

    main_xml_input = full_xml_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
    print(main_xml_input)

    try:
        tree = ET.parse(glob.glob(main_xml_input)[0])
        input_file_log = f'Input XML file = {glob.glob(main_xml_input)[0]}'
        print(input_file_log)
        logging.info(input_file_log)

        root = tree.getroot()
        records = []

        for xml_tuple in root:
            # New record
            record = {}
            for elem in xml_tuple:
                if elem.tag == 'atom' and elem.text:
                    attrib = elem.attrib['name']
                    record[attrib] = elem.text

                # Need to grab SecDepartment as well (start with the first value)
                if elem.tag == 'table' and elem.attrib['name'] == 'SecDepartment_tab':

                    sec_dept_raw = elem.findall('tuple/atom')
                    sec_dept_all = []
                    for dept in sec_dept_raw:
                        if dept.text is not None:
                            if len(dept.text) > 0 and dept.text not in sec_dept_all:
                                if dept.text != " ":
                                    sec_dept_all.append(dept.text)

                    record['SecDepartment'] = sec_dept_all[0]

            if set(['ChaMd5Sum', 'SecDepartment', 'MulIdentifier', 'AudIdentifier']).issubset(record): # or record['AudIdentifier'] is not None:
                records.append(record)
            else:
                log_warn_nofile = f'Skipping MM irn {record["irn"]} -- No ChaMd5Sum or file'
                print(log_warn_nofile)
                logging.warning(log_warn_nofile)

        # Validate our current record set before we proceed
        invalid_records = validate_records(records)
        if invalid_records:
            output_error_log(config, invalid_records)

        # Set up prep_file values
        records_prep_file = []

        for record in records:
            print(record['irn'])
            record_prep = {}
            record_prep['irn'] = record['irn']
            record_prep['MulIdentifier'] = record['MulIdentifier']
            record_prep['AudIdentifier'] = record['AudIdentifier']
            record_prep['prep_file'] = prep_file(record)
            record_prep['pathMove'] = pathmove(record, dept_csv)
            records_prep_file.append(record_prep)

        # # SKIP FIRST 21.1k records
        # records_prep_file = records_prep_file[42700:]


        # Copy all files to correct location, this should happen before we create
        # the CSV to confirm that the files are actually there.
        # If this step fails, raise an exception so the CSV isn't created.
        # copy_files(records_prep_file, full_prefix, dest_prefix, connxn)
        with Connection(host=config['ORIGIN_IP'], user=config['ORIGIN_USER']) as connxn:

            connxn.run('hostname')

            # Copy source-files to staging area & Rename them

            for prep_record in records_prep_file:

                dest_path = dest_prefix + prep_record['pathMove'] + prep_record['prep_file']

                copy_file_to_staging(
                    connxn=connxn,
                    prep_record=prep_record,
                    filename=prep_record['MulIdentifier'],
                    from_prefix=full_prefix,
                    dest_path=dest_path
                    )

                if os.path.isfile(dest_path):
                    if os.path.getsize(dest_path) < 1:

                        file_name = emu_netx.clean_emu_filename(prep_record['MulIdentifier'])

                        copy_file_to_staging(
                            connxn=connxn,
                            prep_record=prep_record,
                            filename=file_name,
                            from_prefix=full_prefix,
                            dest_path=dest_path
                        )

            # Set up fields for CSV
            csv_records = []
            for record in records_prep_file:
                csv_r = {}
                # csv_r['AudIdentifier'] = record['AudIdentifier']
                csv_r['file'] = record['prep_file']
                csv_r['pathMove'] = record['pathMove']
                csv_r['Identifier'] = record['AudIdentifier']
                csv_records.append(csv_r)

            # Validate that the copied files actually exist where we say they
            # do in the prep_file value for the CSV file.
            validate_files_copied(csv_records, dest_prefix)

    except IndexError as idx_err:
        # Account for empty input-dir
        # if len(glob.glob(main_xml_input)) < 1:
        idx_err_msg = f'Error, possible empty input-dir at "{main_xml_input}": {idx_err}'
        print(idx_err_msg)
        logging.error(idx_err_msg)

    # except Exception as err:
    #     err_message = f'An error occurred: {err}'
    #     print(err_message)
    #     logging.error(err_message)

    # Stop logging
    setup.stop_log_dams_netx()


def copy_file_to_staging(
    connxn,
    prep_record:dict,
    filename:str,
    from_prefix:str,
    dest_path:str
    ):
    '''
    Copy file from remote server to staging location
    '''

    dirs = irn_dir(prep_record['irn'])

    full_path = from_prefix + dirs + filename

    # Copy file to the new location for prep_file
    if not os.path.exists(dest_path):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    try:
        connxn.get(remote=full_path, local=dest_path, preserve_mode=False)
        log_message = f'Full origin path = {full_path} | Destination path = {dest_path}'
        print(log_message)
        logging.info(log_message)

        # # Embed dc:identifier in file's XMP (for images/XMP-embeddable formats)
        if os.path.isfile(dest_path):
            if len(re.findall(r'(dng|jpg|jpeg|tif|tiff)+$', dest_path)) > 0:
                with ExifToolHelper() as exif:    # exif.get_tags(dest_path, tags)

                    dest_format = exif.get_tags(dest_path, tags='Format')
                    if len(dest_format) > 0:
                        if ('XMP:Format','image/tiff') in dest_format[0].items():
                            format_warn = f"WARNING - {dest_path} - possible TIFF - check"
                            print(format_warn)
                            logging.warning(format_warn)

                        else:
                            exif.set_tags(
                                dest_path,
                                tags = {'Identifier':prep_record['AudIdentifier']},
                                params=["-m", "-P", "-overwrite_original"]
                            )

    except FileNotFoundError as file_err:
        file_err_msg = f'A file-error occurred trying to copy {full_path}: {file_err}'
        print(file_err_msg)
        logging.error(file_err_msg)

    except exceptions.ExifToolExecuteError as exif_err:
        exif_err_msg = f'An exif-error occurred for {full_path}: {exif_err}'
        print(exif_err_msg)
        logging.error(exif_err_msg)

    except Exception as err:
        err_message = f'An error occurred trying to copy {full_path}: {err}'
        print(err_message)
        logging.error(err_message)


def validate_files_copied(csv_records, dest_prefix):
    """
    Verify that prep_file values are valid, i.e. a file exists at the path.
    """
    for csv_r in csv_records:
        if 'pathAdd' in csv_r.keys():
            path = dest_prefix + csv_r['pathAdd'] + csv_r['file']
        else:    #    if 'pathMove' in r.keys():
            path = dest_prefix + csv_r['pathMove'] + csv_r['file']
        if not os.path.exists(path):
            raise Exception(f'prep_file: {path} does not exist')


def irn_dir(irn):
    """
    Returns the directory structure, given an IRN.
    An IRN needs to be split by the last 3 digits of the IRN, and then the
    remainder of the digits in the first directory. Thus, you will often
    see the first dir with 3-4 digits, while the last dir should always
    have 3 digits.
    """
    digits = list(irn)
    if len(digits) > 3:
        end = digits[-3:]
        del digits[-3:]
        last_dir = ''.join(end)
        first_dir = ''.join(digits)

    # If irn <= 3 digits, dir format is:  0/001 or 0/012 or 0/123
    else:
        first_dir = "0"
        zero_count = 3 - len(digits)
        last_dir = zero_count * '0' + ''.join(digits)

    return f'{first_dir}/{last_dir}/'


def prep_file(record):
    """
    Creates the prepared file-path + file-name value for a record.
    e.g. Active/Multimedia/Geology/Paleobotany/98765_emu_PB1234.jpg

    :param record: dict of the record data
    :return: returns a string of the prep_file value
    """

    filename = record['AudIdentifier']
    file_ext = re.sub(r'(.*)(\..*)', r'\g<2>', record['MulIdentifier'])
    prep_file_name = f'{filename}{file_ext}'
    return prep_file_name


def pathmove(record, dept_csv):
    """
    Creates the pathMove value for a record (folder path without filename)
    e.g. Multimedia/Geology/Paleobotany/

    :param record: dict of the record data
    :return: returns a string of the pathMove value
    """

    department_orig_raw = record['SecDepartment']
    department_orig = department_orig_raw.title()
    if re.match('Amphibian', department_orig) is not None:
        department_orig = "Amphibians and Reptiles"
    department = emu_netx.get_folder_hierarchy(department_orig, dept_csv)

    pathmove_value = f'{department}'
    return pathmove_value


def validate_records(records):
    """
    Before proceeding with the script, validate that every record has all
    of the values in the list.

    Returns ALL invalid records.
    """
    invalid_records = []
    fields_to_validate = ['AudIdentifier', 'irn', 'MulIdentifier', 'SecDepartment']

    for record in records:
        for field in fields_to_validate:
            if field not in record:
                invalid_records.append(record)

    return invalid_records


def output_error_log(config, invalid_records):
    """
    Outputs a CSV of the records that were invalid during XML parsing.

    :param invalid_records: List of invalid records to output
    """

    # To ensure we're not missing any fields for the output,
    # iterate through all of the records, adding any missing fields
    # to the field_names
    field_names = []
    for record in invalid_records:
        keys = record.keys()
        for key in keys:
            if key not in field_names:
                field_names.append(key)

    with open(config['LOG_OUTPUT'] + 'prep_file_prep_errors.csv', mode='w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(invalid_records)

    # raise Exception('Records do not all contain all of the required fields!')

if __name__ == '__main__':
    main()
