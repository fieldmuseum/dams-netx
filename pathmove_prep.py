"""
Things to consider

CSV parsing and writing:
https://realpython.com/python-csv/
"""

# from distutils.command.config import config
import os, sys, csv, shutil
import xml.etree.ElementTree as ET

def main():
  # Main function
  xml_input_file_path = sys.argv[1]
  csv_output_file_path = sys.argv[2]
  use_test_paths = sys.argv[3]

  setup_pathmove(xml_input_file_path, csv_output_file_path, use_test_paths)

def setup_pathmove(xml_input_file_path, csv_output_file_path, use_test_paths):
  """
  Outputs all records' data and copies files into dir for NetX
  Input is an EMu XML export file, outputs to a CSV file with the
  identifier and pathMove.

  :param file_path: filename of the XML file to parse
  :return: list of dictionaries, dictionary includes: AudIdentifier, pathMove
  """

  tree = ET.parse(xml_input_file_path)
  root = tree.getroot()
  records = []

  for xml_tuple in root:
    # New record
    record = {}
    for elem in xml_tuple:
      if elem.tag == 'atom' and elem.text:
        attrib = elem.attrib['name']
        record[attrib] = elem.text
      # Need to grab SecDepartment as well
      if elem.tag == 'table' and elem.attrib['name'] == 'SecDepartment_tab':
        sec_dept_tuple_elem = elem.find('tuple')
        sec_dept = sec_dept_tuple_elem.find('atom')
        record['SecDepartment'] = sec_dept.text
    records.append(record)
  
  # Validate our current record set before we proceed
  invalid_records = validate_records(records)
  if invalid_records: output_error_log(invalid_records)

  # Set up pathMove values
  records_pathmove = []
  for record in records:
    r = {}
    r['irn'] = record['irn']
    r['MulIdentifier'] = record['MulIdentifier']
    r['AudIdentifier'] = record['AudIdentifier']
    r['pathMove'] = pathmove(record)
    records_pathmove.append(r)

  # Copy all files to correct location, this should happen before we create
  # the CSV to confirm that the files are actually there.
  # If this step fails, raise an exception so the CSV isn't created.
  copy_files(records_pathmove, use_test_paths)

  # Set up fields for CSV
  csv_records = []
  for record in records_pathmove:
    r = {}
    r['AudIdentifier'] = record['AudIdentifier']
    r['pathMove'] = record['pathMove']
    csv_records.append(r)

  # Validate that the copied files actually exist where we say they
  # do in the pathMove value for the CSV file.
  validate_files_copied(csv_records)

  # FINAL STEP: Write records to CSV
  with open(csv_output_file_path, mode='w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=['AudIdentifier', 'pathMove'])
    writer.writeheader()
    writer.writerows(csv_records)

def copy_files(records, use_test_paths):
  """
  Given a list of records, copy all of the files to the new location required
  for the pathMove value that will end up in the CSV file.
  """
  for r in records:
    dirs = irn_dir(r['irn'])
    if use_test_paths == True:
      full_prefix = os.getenv('TEST_ORIGIN_PATH')
      dest_prefix = os.getenv('TEST_DESTIN_PATH')
    else: 
      full_prefix = os.getenv('ORIGIN_PATH')
      dest_prefix = os.getenv('DESTIN_PATH')

    full_path = full_prefix + dirs + r['MulIdentifier']
    dest_path = dest_prefix + r['pathMove']

    # copy file to the new location for pathMove
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if not os.path.exists(dest_path): shutil.copy2(full_path, dest_path)

def validate_files_copied(csv_records):
  """
  Verify that pathMove values are valid, i.e. a file exists at the path.
  """
  base_path = os.getenv('DESTIN_PATH')
  for r in csv_records:
    path = base_path + r['pathMove']
    if not os.path.exists(path):
      raise Exception(f'pathMove: {path} does not exist')

def irn_dir(irn):
  """
  Returns the directory structure, given an IRN.
  An IRN needs to be split by the last 3 digits of the IRN, and then the
  remainder of the digits in the first directory. Thus, you will often
  see the first dir with 3-4 digits, while the last dir should always
  have 3 digits. This could get problematic for super low IRN values.
  We will have to ensure this code still works for those values.
  """
  digits = list(irn)
  if len(digits) > 3:
    end = digits[-3:]
    del digits[-3:]
    last_dir = ''.join(end)
    first_dir = ''.join(digits)
  
  # If irn <= 3 digits, dir format is:  0/001 or 0/012 or 0/123
  elif len(digits) <= 3:
    first_dir = "0"
    zero_count = 3 - len(digits)
    last_dir = zero_count * '0' + ''.join(digits)

  return f'{first_dir}/{last_dir}/'

def pathmove(record):
  """
  Creates the pathMove value for a record.
  e.g. Active/Multimedia/Paleobotany/98765_emu_PB1234.jpg

  :param record: dict of the record data
  :return: returns a string of the pathMove value
  """
  status = record['SecRecordStatus']
  record_type = 'Multimedia'
  department = record['SecDepartment']
  irn = record['irn']
  filename = record['MulIdentifier']
  pathmove = f'{status}/{record_type}/{department}/{irn}_emu_{filename}'
  return pathmove

def validate_records(records):
  """
  Before proceeding with the script, validate that every record has all
  of the values in the list.

  Returns ALL invalid records.
  """
  invalid_records = []
  fields_to_validate = ['irn', 'MulIdentifier', 'SecRecordStatus', 'SecDepartment']

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

  with open('data/errors/pathmove_prep_errors.csv', mode='w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(invalid_records)
  raise Exception('Records do not all contain all of the required fields!')

if __name__ == '__main__':
  main()
