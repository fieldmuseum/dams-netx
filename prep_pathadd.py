"""
Setup the NetX pathAdd CSV
"""

import glob
import logging
import re
import sys
# from decouple import config
import xml.etree.ElementTree as ET
from utils import csv_tools as uc
from utils import setup
from utils import emu_netx_map as emu_netx


def main():
    """
    Outputs all records' data and copies files into dir for NetX
    Input is an EMu XML export file, outputs to a CSV file with the
    filename (identifier + file-extension) and filepath (prep_file).

    :param file_path: filename of the XML file to parse
    :return: list of dictionaries, dictionary includes: AudIdentifier, prep_file
    """

    # Start logs
    setup.start_log_dams_netx(config=None, cmd_args=sys.argv)

    # Main function
    live_or_test, input_date = setup.get_sys_argv(2)

    config = setup.get_config_dams_netx(live_or_test)

    csv_output_file_path = config['PATHADD_CSV_FILE']
    dept_csv = config['DEPARTMENT_CSV']

    # Check if test or live paths should be used
    # if live_or_test == "LIVE":
    #     full_xml_prefix = config['ORIGIN_PATH_XML']
    # else:
    #     full_xml_prefix = config['TEST_ORIGIN_PATH_XML']
    full_xml_prefix = setup.get_path_from_env(
        live_or_test,
        config['ORIGIN_PATH_XML'],
        config['TEST_ORIGIN_PATH_XML']
        )

    main_xml_input = full_xml_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
    input_path_log = f'Input XML full path = {main_xml_input}'
    print(input_path_log)
    logging.info(input_path_log)

    input_file_log = f'Input XML file = {glob.glob(main_xml_input)[0]}'
    print(input_file_log)
    logging.info(input_file_log)


    # TODO - test/try to account for empty input-dir
    tree = ET.parse(glob.glob(main_xml_input)[0])

    root = tree.getroot()
    records = []
    path_add_running_list = []

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

                # Get secondary SecDepartment values for pathAdd
                if len(sec_dept_all) > 1:
                    record['PathAddDepts'] = sec_dept_all
                else:
                    record['PathAddDepts'] = None

        if 'ChaMd5Sum' in record.keys():
            records.append(record)
        else:
            log_warn_nofile = f"Skipping {record['AudIdentifier']} -- No MD5 sum (ChaMd5Sum) / no file"
            print(log_warn_nofile)
            logging.warning(log_warn_nofile)

    # Validate our current record set before we proceed
    invalid_records = validate_records(records)
    if invalid_records:
        output_error_log(invalid_records)

    # Set up prep_file values

    path_add_running_list = []
    records_prep_file = []

    for record in records:
        record_prep = {}
        record_prep['irn'] = record['irn']
        record_prep['MulIdentifier'] = record['MulIdentifier']
        record_prep['AudIdentifier'] = record['AudIdentifier']
        record_prep['prep_file'] = prep_file(record)
        record_prep['pathMove'] = pathmove(record, dept_csv)
        records_prep_file.append(record_prep)

        if record['PathAddDepts'] is not None:    # len(sec_dept_others) > 1:
            path_add_rows = pathadd(record, dept_csv)
            for row in path_add_rows[1:]:
                path_add_running_list.append(row)


    # FINAL STEP: Write pathAdd rows to CSV
    if len(path_add_running_list) > 0:
        output_log = f'outputing pathAdd CSV to {csv_output_file_path}'
        print(output_log)
        logging.info(output_log)

        field_names = path_add_running_list[0].keys()

        uc.write_list_of_dict_to_csv(path_add_running_list, field_names, csv_output_file_path)

    else:
        no_pathadd = 'No pathAdd required -- All assets in single folders.'
        print(no_pathadd)
        logging.info(no_pathadd)

    # Stop logging
    setup.stop_log_dams_netx()


# def get_folder_hierarchy(department_raw:str, dept_csv:str):
#     '''
#     Get the appropriate parent-folder value for a given SecDepartment value
#     '''
#     dept_csv = dept_csv  # config('DEPARTMENT_CSV')
#     dept_folders = []
#     with open(dept_csv, encoding='utf-8', mode = 'r') as csvfile:
#         reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
#         for r in reader: dept_folders.append(r)

#     # make lists of level_1 & level_2 values
#     # NOTE - NOT unique lists; a value's index will be used to get the corresponding parent
#     dept_emu = []
#     for row in dept_folders: dept_emu.append(row['emu'])

#     dept_level_1 = []
#     for row in dept_folders: dept_level_1.append(row['netx_level_1'])

#     dept_level_2 = []
#     for row in dept_folders: dept_level_2.append(row['netx_level_2'])

#     department = department_raw.strip()

#     if department in dept_level_2:
#         # lookup level_1 value at same index for level_2 key/value
#         parent = dept_level_1[dept_level_2.index(department)]
#         return parent + '/' + department + '/'

#     else:
#         # return department + '/'
#         return dept_level_1[dept_emu.index(department)]


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

    # If irn <= 3 digits, dir format is:    0/001 or 0/012 or 0/123
    else:    # elif len(digits) <= 3:
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


def pathmove(record:dict, dept_csv:str):
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


def pathadd(record:dict, dept_csv:str):
    """
    Creates the pathAdd value(s) for a record (folder path without filename)
    e.g.
    [
        {'file':identifier-123-abc.jpg, 'pathAdd':'Multimedia/Geology/Paleobotany/'},
        {'file':identifier-123-abc.jpg, 'pathAdd':'Multimedia/Library/Photo Archives/'}
    ]

    :param record: dict of the record data
    :return: returns a list of dicts with an asset's pathAdd rows
    """
    path_add_list = []

    filename = prep_file(record)

    for dept_raw in record['PathAddDepts']:
        if dept_raw is not None:
            dept = dept_raw.title()
            if re.match('Amphibian', dept) is not None:
                dept = "Amphibians and Reptiles"
            dept_folder = emu_netx.get_folder_hierarchy(dept, dept_csv)
            pathadd_folder = f'{dept_folder}'
            path_add_row = {'file':filename, 'pathAdd':pathadd_folder}

            if path_add_row not in path_add_list:
                path_add_list.append(path_add_row)

    if len(path_add_list) > 0:
        return path_add_list


def validate_records(records):
    """
    Before proceeding with the script, validate that every record has all
    of the values in the list.

    Returns ALL invalid records.
    """
    invalid_records = []
    fields_to_validate = [
        'AudIdentifier',
        'irn',
        'MulIdentifier',
        'SecRecordStatus',
        'SecDepartment'
        ]

    for record in records:
        for field in fields_to_validate:
            if field not in record:
                invalid_records.append(record)

    return invalid_records


def output_error_log(invalid_records):
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

    filename = 'data/errors/prep_file_prep_errors.csv'

    uc.write_list_of_dict_to_csv(invalid_records, field_names, filename)


if __name__ == '__main__':
    main()
