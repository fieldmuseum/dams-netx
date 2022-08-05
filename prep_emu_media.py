"""
Rename files and copy them to NetX Multimedia folder-structure

CSV parsing and writing:
https://realpython.com/python-csv/
"""

import csv, os, re, sys
from decouple import config
from exiftool import ExifToolHelper
from fabric import Connection
import xml.etree.ElementTree as ET


def main():
  """
  Outputs all records' data and copies files into dir for NetX
  Input is an EMu XML export file, outputs to a CSV file with the
  filename (identifier + file-extension) and filepath (prep_file).

  :param file_path: filename of the XML file to parse
  :return: list of dictionaries, dictionary includes: AudIdentifier, prep_file
  """

  # Main function
  input_date = sys.argv[1]  # match this to prep_emu_xml?: xml_input_file_path = full_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
  csv_output_file_path = sys.argv[2]
  use_live_paths = sys.argv[3]
  
  # Check if test or live paths should be used
  if use_live_paths == "LIVE":
    full_prefix = config('ORIGIN_PATH_MEDIA')
    dest_prefix = config('DESTIN_PATH_MEDIA')
  else: 
    full_prefix = config('TEST_ORIGIN_PATH_MEDIA')
    dest_prefix = config('TEST_DESTIN_PATH_MEDIA')
  
  # with Connection(host=config('ORIGIN_IP'), user=config('ORIGIN_USER')) as c:
  
  main_xml_input = full_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
  #   c.run('hostname')

  #   # # Copy source-files to staging area & rename them
  #   # setup_prep_file(xml_input_file_path, csv_output_file_path, full_prefix, dest_prefix, c)


  # def setup_prep_file(xml_input_file_path, csv_output_file_path, full_prefix, dest_prefix, c):

  tree = ET.parse(main_xml_input[0])
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

      # Need to grab SecDepartment as well (currently: use only the first value)
      if elem.tag == 'table' and elem.attrib['name'] == 'SecDepartment_tab':
        sec_dept_tuple_elem = elem.find('tuple')
        sec_dept = sec_dept_tuple_elem.find('atom')
        record['SecDepartment'] = sec_dept.text

        # Get secondary SecDepartment values for pathAdd
        sec_dept_others = elem.findall('tuple/atom')
        if len(sec_dept_others) > 1:
          record['PathAddDepts'] = sec_dept_others
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

    if record['PathAddDepts'] is not None:  # len(sec_dept_others) > 1:
      path_add_rows = pathadd(record)  # pathadd(record)
      for row in path_add_rows:
        path_add_running_list.append(row)

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
        print(f'Full origin path = {full_path} | Destination path = {dest_path}')
      except Exception as err:
        print(f'An error occurred trying to copy media from {full_path}: {err}')
      
      # # Embed dc:identifier in file's XMP (for images/XMP-embeddable formats)
      if os.path.isfile(dest_path):
        if len(re.findall(r'(dng|jpg|jpeg|tif|tiff)+$', dest_path)) > 0:
          with ExifToolHelper() as exif:
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
        # writer = csv.DictWriter(csv_file, fieldnames=csv_records[0].keys() )  # ['file', 'pathMove'])
        field_names=path_add_running_list[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=field_names )
        writer.writeheader()
        # writer.writerows(csv_records)
        writer.writerows(path_add_running_list)


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


# def copy_files(records, full_prefix, dest_prefix, c):
#   """
#   Given a list of records, copy all of the files to the new location required
#   for the prep_file value that will end up in the CSV file.
#   """
#   for r in records:
#     dirs = irn_dir(r['irn'])

#     full_path = full_prefix + dirs + r['MulIdentifier']
#     dest_path = dest_prefix + r['pathMove']  # + r['prep_file']

#     # # copy file to the new location for prep_file
#     if not os.path.exists(dest_path):
#       os.makedirs(os.path.dirname(dest_path), exist_ok=True)    
    
#     try:
#       # media_file_loc = full_prefix + config('ORIGIN_MEDIA_EXAMPLE_FILE_LOC')
#       c.get(remote=full_path, local=dest_prefix, preserve_mode=False)
#       print(f'Full origin path = {full_path} | Dest base-prefix = {dest_prefix}')
#     except Exception as err:
#       print(f'An error occurred trying to copy media from {full_path}: {err}')

#     # if not os.path.exists(dest_path): 
#     #   shutil.copy2(full_path, dest_path)



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
  else:  # elif len(digits) <= 3:
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

  # irn = record['irn']
  # filename = record['MulIdentifier']
  filename = record['AudIdentifier']
  file_ext = re.sub(r'(.*)(\..*)', r'\g<2>', record['MulIdentifier'])
  # prep_file = f'{irn}_emu_{filename}' # f'{status}/{record_type}/{department}/{irn}_emu_{filename}'
  prep_file = f'{filename}{file_ext}'
  return prep_file
  

def pathmove(record):
  """
  Creates the pathMove value for a record (folder path without filename)
  e.g. Multimedia/Geology/Paleobotany/

  :param record: dict of the record data
  :return: returns a string of the pathMove value
  """
  # status = record['SecRecordStatus']
  # record_type = 'Multimedia'
  
  department_orig = record['SecDepartment']
  department = get_folder_hierarchy(department_orig)

  # pathmove = f'{status}/{record_type}/{department}'
  # pathmove = f'{record_type}/{department}'  
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
  record_type = 'Multimedia'
  path_add_list = []
  
  filename = prep_file(record)

  # other_departments_orig = record['PathAddDepts']
  # other_departments = other_departments_orig.split("|")

  # if len(other_departments) == 1:
  #   return None

  # elif len(other_departments) > 1:

  # record['PathAddDepts'] should be a list of ET.Element
  for dept in record['PathAddDepts']:
    dept_folder = get_folder_hierarchy(dept.text)
    pathadd = f'{record_type}/{dept_folder}'
    path_add_row = {'file':filename, 'pathAdd':pathadd}

    if path_add_row not in path_add_list:
      # print('adding other dept: ' + str(pathadd))
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
