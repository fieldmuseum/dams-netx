"""
Rename files and copy them to NetX Multimedia folder-structure

CSV parsing and writing:
https://realpython.com/python-csv/
"""

import csv, glob, logging, os, re, sys
from decouple import config
from exiftool import ExifToolHelper
from fabric import Connection
import xml.etree.ElementTree as ET
import utils.setup as setup


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
  input_date = sys.argv[1]  # match this to prep_emu_xml?: xml_input_file_path = full_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
  csv_output_file_path = sys.argv[2]
  use_live_paths = sys.argv[3]
  
  # Check if test or live paths should be used
  if use_live_paths == "LIVE":
    full_prefix = config('ORIGIN_PATH_MEDIA')
    full_xml_prefix = config('ORIGIN_PATH_XML')
    dest_prefix = config('DESTIN_PATH_MEDIA')
  else: 
    full_prefix = config('TEST_ORIGIN_PATH_MEDIA')
    full_xml_prefix = config('TEST_ORIGIN_PATH_XML')
    dest_prefix = config('TEST_DESTIN_PATH_MEDIA')
  
  # with Connection(host=config('ORIGIN_IP'), user=config('ORIGIN_USER')) as c:
  
  main_xml_input = full_xml_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
  print(main_xml_input)

  tree = ET.parse(glob.glob(main_xml_input)[0])  # TODO - test/try to account for empty input-dir

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
              sec_dept_all.append(dept.text)

        record['SecDepartment'] = sec_dept_all[0]

        # Get secondary SecDepartment values for pathAdd
        if len(sec_dept_all) > 1:
          record['PathAddDepts'] = sec_dept_all
        else:
          record['PathAddDepts'] = None
        
    records.append(record)
  
  # Validate our current record set before we proceed
  invalid_records = validate_records(records)
  if invalid_records: output_error_log(invalid_records)

  # Set up prep_file values  
  path_add_running_list = []  
  records_prep_file = []

  for record in records:
    r = {}
    r['irn'] = record['irn']
    r['MulIdentifier'] = record['MulIdentifier']
    r['AudIdentifier'] = record['AudIdentifier']
    r['prep_file'] = prep_file(record)
    r['pathMove'] = pathmove(record)
    records_prep_file.append(r)

    if record['PathAddDepts'] is not None: 
      path_add_rows = pathadd(record)
      for row in path_add_rows:
        path_add_running_list.append(row)
    

  # # SKIP FIRST 21.1k records 
  # records_prep_file = records_prep_file[21100:]


  # Copy all files to correct location, this should happen before we create
  # the CSV to confirm that the files are actually there.
  # If this step fails, raise an exception so the CSV isn't created.
  # copy_files(records_prep_file, full_prefix, dest_prefix, c)

  with Connection(host=config('ORIGIN_IP'), user=config('ORIGIN_USER')) as c:
  
    c.run('hostname')

    # Copy source-files to staging area & Rename them

    for r in records_prep_file:
      dirs = irn_dir(r['irn'])

      full_path = full_prefix + dirs + r['MulIdentifier']
      dest_path = dest_prefix + r['pathMove'] + r['prep_file']

      # # copy file to the new location for prep_file
      if not os.path.exists(dest_path):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)    
      
      try:
        c.get(remote=full_path, local=dest_path, preserve_mode=False)
        log_message = f'Full origin path = {full_path} | Destination path = {dest_path}'
        print(log_message)
        logging.info(log_message)

      except Exception as err:
        err_message = f'An error occurred trying to copy media from {full_path}: {err}'
        print(err_message)
        logging.error(err_message)
      
      # # Embed dc:identifier in file's XMP (for images/XMP-embeddable formats)
      if os.path.isfile(dest_path):
        if len(re.findall(r'(dng|jpg|jpeg|tif|tiff)+$', dest_path)) > 0:
          with ExifToolHelper() as exif:  # exif.get_tags(dest_path, tags)
            
            dest_format = exif.get_tags(dest_path, tags='Format')
            if len(dest_format) > 0:
              if ('XMP:Format','image/tiff') in dest_format[0].items():
                format_warn = f"WARNING - {dest_path} - possible TIFF File - needs check/fix in EMu"
                print(format_warn)
                logging.warning(format_warn)

              else:
                exif.set_tags(
                  dest_path,
                  tags = {'Identifier':r['AudIdentifier']},
                  params=["-P", "-overwrite_original"]
                )


    # Set up fields for CSV
    csv_records = []
    for record in records_prep_file:
      r = {}
      # r['AudIdentifier'] = record['AudIdentifier']
      r['file'] = record['prep_file']
      r['pathMove'] = record['pathMove']
      r['Identifier'] = record['AudIdentifier']
      csv_records.append(r)

    # Validate that the copied files actually exist where we say they
    # do in the prep_file value for the CSV file.
    validate_files_copied(csv_records, dest_prefix)

    # FINAL STEP: Write pathAdd rows to CSV
    # print("len for pathAdd list = " + str(len(path_add_running_list)))
    if len(path_add_running_list) > 0:
      with open(csv_output_file_path, mode='w') as csv_file:
        field_names=path_add_running_list[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=field_names )
        writer.writeheader()
        writer.writerows(path_add_running_list)


  # Stop logging
  setup.stop_log_dams_netx()


def get_folder_hierarchy(department):
  '''
  Get the appropriate parent-folder value for a given SecDepartment value
  '''
  dept_csv = config('DEPARTMENT_CSV')
  dept_folders = []
  with open(dept_csv, encoding='utf-8', mode = 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for r in reader: dept_folders.append(r)

  # make lists of level_1 & level_2 values
  # NOTE - NOT unique lists; a value's index will be used to get the corresponding parent
  dept_level_1 = []
  for row in dept_folders: dept_level_1.append(row['level_1'])

  dept_level_2 = []
  for row in dept_folders: dept_level_2.append(row['level_2'])

  if department in dept_level_2:
    # lookup level_1 value at same index for level_2 key/value
    parent = dept_level_1[dept_level_2.index(department)]
    return parent + '/' + department + '/'
  
  else: return department + '/'


def validate_files_copied(csv_records, dest_prefix):
  """
  Verify that prep_file values are valid, i.e. a file exists at the path.
  """
  for r in csv_records:
    if 'pathAdd' in r.keys():
      path = dest_prefix + r['pathAdd'] + r['file']
    else:  #  if 'pathMove' in r.keys():
      path = dest_prefix + r['pathMove'] + r['file']
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
  prep_file = f'{filename}{file_ext}'
  return prep_file
  

def pathmove(record):
  """
  Creates the pathMove value for a record (folder path without filename)
  e.g. Multimedia/Geology/Paleobotany/

  :param record: dict of the record data
  :return: returns a string of the pathMove value
  """
  
  department_orig = record['SecDepartment']
  department = get_folder_hierarchy(department_orig)

  pathmove = f'{department}'
  return pathmove


def pathadd(record: dict):
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

  # record['PathAddDepts'] should be a list of ET.Element
  for dept in record['PathAddDepts']:
    if dept is not None:
      dept_folder = get_folder_hierarchy(dept)
      pathadd = f'{dept_folder}'
      path_add_row = {'file':filename, 'pathAdd':pathadd}

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
  fields_to_validate = ['AudIdentifier', 'irn', 'MulIdentifier', 'SecRecordStatus', 'SecDepartment']

  for record in records:
    for field in fields_to_validate:
      if field not in record: invalid_records.append(record)

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
  for r in invalid_records:
    keys = r.keys()
    for key in keys:
      if key not in field_names: field_names.append(key)

  with open('data/errors/prep_file_prep_errors.csv', mode='w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(invalid_records)

  raise Exception('Records do not all contain all of the required fields!')

if __name__ == '__main__':
  main()
