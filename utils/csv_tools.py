'''CSV tools'''

import csv

def rows(file: str) -> list:
    '''Returns a list of rows (dicts) from an input CSV file'''
    rows = []
    with open(file, encoding='utf-8', mode = 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for r in reader: rows.append(r)

    return rows

def write_list_of_dict_to_csv(input_records:list, field_names:list, output_csv_file_name:str):
    '''Outputs a CSV file for a list of dictionaries, with given field-names'''

    with open(output_csv_file_name, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, extrasaction='ignore', fieldnames=field_names)
        writer.writeheader()
        writer.writerows(input_records)

    # raise Exception('Records do not all contain all of the required fields!')