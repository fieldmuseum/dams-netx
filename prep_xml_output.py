# Prep dictionaries for output json
from glob import glob
import sys


def prep_output_dict(emu_mapping, map_conditions):
    # # # # # # # # # # # # # # # # #
    # Single (Un-grouped) h2i fields
    
    # Try filtering/appending fields into groups at end. Otherwise, include in each field-type loop [slow?]
    # TO DO: differentiate between data-types for repeatable [] and non-repeatable "" in schema; currently all repeatable []
    json_single_emu = emu_mapping[emu_mapping['json_container'].isnull()]['json_field'].values
    json_single_map = map_conditions[map_conditions['json_container'].isnull()]['json_field'].values

    single_dict = dict()
    for single_emu in json_single_emu:
        single_dict[single_emu] = []

    for single_map in json_single_map:
        single_dict[single_map] = []


    # # # # # # # # # # # # # # # # #
    # Grouped h2i fields
    json_groups = emu_mapping[emu_mapping['json_container'].notnull()]['json_container'].values
    # json_con_groups = map_condition['json_container'].values  # Safe to assume all container-values show in emu_map?

    for group_key in json_groups:

        single_dict[group_key] = []

    return single_dict


# To run convert_xml.py directly, run:
#   python3 convert_xml.py file1 file2 etc
if __name__ == '__main__':
    for arg in sys.argv[1:]:
        for filename in glob(arg):
            prep_output_dict(arg)