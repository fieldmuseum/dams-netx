'''
Parse EMu XML to DAMS-ready XML
2022-Jun; FMNH, based on EMu-xml-to-json convert_xml.py
'''

import glob
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
# from decouple import config
from utils import dss_schema
from utils import xml_tools
from utils import emu_netx_map as emu_netx
from utils import setup


def parse_emu_to_dss(
    emu_record: ET.Element,
    mm_event: ET.Element,
    mm_catalog: ET.Element,
    mm_exob_mul: ET.Element,
    mm_exob_ins: ET.Element,
    conditions:list) -> ET.Element:
    '''Parse exported EMu records to DSS-schema records'''

    print(emu_record.find('irn').text)

    # Setup record's DSS fields
    prepped_record = dss_schema.media_schema_xml()

    # Add NetxFilename field as key / remap AudIdentifier
    file_ext = re.sub(r'(.*)(\..{2,4}$)', r'\g<2>', emu_record.find('MulIdentifier').text)
    prepped_record.find('NetxFilename').text = emu_record.find('AudIdentifier').text + file_ext


    # Populate DSS fields for atomic EMu fields:
    atomic_fields = emu_netx.emu_netx_atoms()

    for key, value in atomic_fields.items():
        if value is not None and emu_record.find(value) is not None:
            prepped_record.find(key).text = emu_record.find(value).text

            if key == "AudAssociatedSpecimen" and prepped_record.find(key).text is not None:
                guid = prepped_record.find(key).text
                prepped_record.find(key).text = f'https://db.fieldmuseum.org/{guid}'


    # Populate DSS fields with conditional values
    for condition in conditions:

        # handle fields conditionally MAPPED to another field
        if condition['then_logic'] == 'MAP':
            emu_condition_value = xml_tools.get_conditional_group_value(
                emu_record=emu_record,
                group_tag=condition['if_group1'],
                child_if_tag=condition['if_field1'],
                child_if_logic=condition['if_logic1'],
                child_if_value=condition['if_value1'],
                child_then_field=condition['then_field'],
                child_then_value=condition['then_value']
            )

            prepped_record.find(condition['then_field']).text = emu_condition_value
        
        # handle fields with conditional STATIC values
        elif condition['then_logic'] == 'STATIC':
            prepped_record.find(condition['then_field']).text = condition['then_value']
            


    # Populate table-fields
    table_fields = emu_netx.emu_netx_tables()

    for key, value in table_fields.items():
        if isinstance(value, list):
            print('figure this out')

        elif value is not None and emu_record.find(value) is not None:
            # This pulls the concatenated value from convert_linebreaks_to_commas()
            prepped_record.find(key).text = emu_record.find(value).text


    # Populate single-reference-fields (e.g. DetMediaRightsRef)
    ref_fields = emu_netx.emu_netx_refs()

    for key, value in ref_fields.items():

        if isinstance(value, list):
            ref_values = xml_tools.get_ref_value(emu_record, value[0], value[1])
            if ref_values is not None: # and re.match(r'^\s+$', ref_values) is None:
                prepped_record.find(key).text = ref_values
            else:
                prepped_record.find(key).text = ''

    # Populate grouped or ref-table fields with nested tuples
    #   (e.g. 'Creator' group, rev-attached Catalog fields)
    group_fields = emu_netx.emu_netx_groups_or_reftabs()

    for key, value in group_fields.items():
        if isinstance(value, list):

            grouped_value = None

            if key in ['CatDepartment', 'CatCatalog'] and mm_catalog is not None:
                grouped_value = xml_tools.get_unique_group_value(mm_catalog, value[0], value[1])

            elif key.find('ExOb_') > -1:

                # Loop through prioritized group first (e.g. 'Install' tab vs main 'MM' tab):
                if mm_exob_ins is not None:
                    if value[1].find('.') > -1:
                        grouped_value = xml_tools.get_unique_group_ref_value(mm_exob_ins, value[0][0], value[1])

                    elif type(value[0]) is list:
                        grouped_value = xml_tools.get_unique_group_ref_value(mm_exob_ins, value[0][0], value[1], False)

                    else:
                        grouped_value = xml_tools.get_group_value(mm_exob_ins, value[0], value[1])

                # Only use ExOb main MM tab if MM is only attached on main MM
                if grouped_value is None or grouped_value == '':

                    if value[1].find('.') > -1:
                        grouped_value = xml_tools.get_unique_group_ref_value(mm_exob_ins, value[0][1], value[1])

                    elif type(value[0]) is list:
                        grouped_value = xml_tools.get_unique_group_ref_value(mm_exob_mul, value[0][1], value[1], False)

                    else:
                        grouped_value = xml_tools.get_group_value(mm_exob_mul, value[0], value[1])  

            else:
                grouped_value = xml_tools.get_group_value(emu_record, value[0], value[1])

            if grouped_value is not None:
                prepped_record.find(key).text = grouped_value


    # Populate fields where values need concatenation (e.g. reverse-attached Event fields)
    concat_fields = emu_netx.emu_netx_ref_concatenate()

    for key,value in concat_fields.items():

        # TODO - loop through for multiple reverse-attachments of one kind
        #   (e.g. if >1 rev-attached Event records)

        concat_values = None

        if isinstance(value, list):
            if isinstance(value[1], list):
                if mm_event is not None and len(mm_event.findall('.//' + value[1][0])) > 0:
                    concat_values_raw = []

                    for field_name in value[1]:
                        concat_value = mm_event.find('.//' + field_name).text
                        if concat_value is None:
                            concat_value = 'NULL, check EMu'

                        concat_values_raw.append(concat_value)

                    concat_values = ' | '.join(concat_values_raw)
                    prepped_record.find(key).text = concat_values

            elif key == 'EveEventURLs':
                if mm_event is not None and len(mm_event.findall('.//' + value[1])) > 0:
                    pj_guid = mm_event.find('.//' + value[1]).text
                    prepped_record.find(key).text = f'https://pj.fieldmuseum.org/event/{pj_guid}'


    return prepped_record


def main():  # main_xml_input, event_xml, catalog_xml):
    '''Given an input-date, prep XML export from that date'''

    # Main function

    # Setup paths to input XML
    live_or_test, input_date = setup.get_sys_argv(2)

    config = setup.get_config_dams_netx(live_or_test)

    # Start logs
    setup.start_log_dams_netx(config=config, cmd_args=sys.argv)

    # # Check if test or live paths should be used
    # if live_or_test == "LIVE":
    #     full_prefix = config['ORIGIN_PATH_XML']
    #     dest_prefix = config['DESTIN_PATH_XML']
    # else:  # if live_or_test == "TEST":
    #     full_prefix = config['TEST_ORIGIN_PATH_XML']
    #     dest_prefix = config['TEST_DESTIN_PATH_XML']
    full_prefix = setup.get_path_from_env(
        live_or_test,
        config['ORIGIN_PATH_XML'],
        config['TEST_ORIGIN_PATH_XML']
        )
    dest_prefix = setup.get_path_from_env(
        live_or_test,
        config['DESTIN_PATH_XML'],
        config['TEST_DESTIN_PATH_XML']
        )

    main_xml_input = full_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
    event_xml = full_prefix + 'NetX_mm_events/' + input_date + '/xml*'
    catalog_xml = full_prefix + 'NetX_mm_catalogue/' + input_date + '/xml*'
    exobj_mul_xml = full_prefix + 'NetX_mm_exhobj_mm/' + input_date + '/xml*'
    exobj_ins_xml = full_prefix + 'NetX_mm_exhobj_install/' + input_date + '/xml*'

    conditions = emu_netx.get_emu_netx_conditions(config['CONDITIONS_CSV'])

    input_file_log = f'Input XML file = {glob.glob(main_xml_input)[0]}'
    print(input_file_log)
    logging.info(input_file_log)

    # Load EMu records & fix xml-tags
    emu_tree = ET.ElementTree()

    # TODO - test/try to account for empty input-dir
    emu_records_raw1 = emu_tree.parse(glob.glob(main_xml_input)[0])

    emu_records_raw2 = xml_tools.fix_emu_xml_tags(emu_records_raw1)
    emu_records = xml_tools.convert_linebreaks_to_commas(emu_records_raw2)


    # Import attachmen exports too: Events, Catalog, Exh.Objects (Mul & Ins tabs)
    eve_raw1 = xml_tools.get_input_xml(event_xml, input_date)
    cat_raw1 = xml_tools.get_input_xml(catalog_xml, input_date)
    exobj_mul_raw1 = xml_tools.get_input_xml(exobj_mul_xml, input_date)
    exobj_ins_raw1 = xml_tools.get_input_xml(exobj_ins_xml, input_date)

    eve_records_raw2 = xml_tools.fix_emu_xml_tags(eve_raw1)
    cat_records_raw2 = xml_tools.fix_emu_xml_tags(cat_raw1)
    exobj_mul_records_raw2 = xml_tools.fix_emu_xml_tags(exobj_mul_raw1)
    exobj_ins_records_raw2 = xml_tools.fix_emu_xml_tags(exobj_ins_raw1)

    # Prep DSS output as ET Element -- appendable, similar to a [list]
    dss_records = ET.Element('emultimedia')

    # # smaller test-set
    # emu_records = emu_records[:10]


    # loop through & prep EMu records
    for emu_record in emu_records:

        # grab corresponding Event & Catalog, if any:
        mm_event = None
        mm_catalog = None
        mm_exob_mul = None
        mm_exob_ins = None

        if None in [emu_record.find('AudIdentifier').text, emu_record.find('MulIdentifier').text, emu_record.find('ChaMd5Sum').text]:
            log_warn_nofile = f'Skipping {emu_record.find("AudIdentifier").text} -- No MD5 sum (ChaMd5Sum) / no file'
            print(log_warn_nofile)
            logging.warning(log_warn_nofile)

        else:

            for event_record in eve_records_raw2:
                if event_record.find('AudIdentifier').text == emu_record.find('AudIdentifier').text:
                    if event_record.findall('AdmGUIDValue') is not None:
                        mm_event = event_record
                        # print("event = " + str(mm_event.findall('./')))

            for cat_record in cat_records_raw2:
                if cat_record.find('AudIdentifier').text == emu_record.find('AudIdentifier').text:
                    mm_catalog = cat_record
            
            for exob_mul_record in exobj_mul_records_raw2:
                if exob_mul_record.find('AudIdentifier').text == emu_record.find('AudIdentifier').text:
                    mm_exob_mul = exob_mul_record

            for exob_ins_record in exobj_ins_records_raw2:
                if exob_ins_record.find('AudIdentifier').text == emu_record.find('AudIdentifier').text:
                    mm_exob_ins = exob_ins_record


            # loop thru dss schema fields & populate from EMu xml
            if emu_record.find('MulIdentifier').text is not None and emu_record.find('ChaMd5Sum').text is not None:
                prepped_record = parse_emu_to_dss(
                    emu_record,
                    mm_event,
                    mm_catalog,
                    mm_exob_mul,
                    mm_exob_ins,
                    conditions
                    )

                if prepped_record is not None:
                    dss_records.append(prepped_record)


    # Output Prepped DSS-XML
    print("# of dss_records is :  " + str(len(dss_records)) + " | output to: " + dest_prefix)
    if len(dss_records) > 1:
        if os.path.exists(dest_prefix) is False:
            os.makedirs(dest_prefix)

        with open(dest_prefix + "dss_prepped.xml", 'wb') as output_file:
            output_file.write(
                ET.tostring(
                    dss_records,
                    xml_declaration=True,
                    encoding='utf-8',
                    short_empty_elements=True
                    )
                )

    setup.stop_log_dams_netx()


    # if output_emu_prepped == True:

    #     emu_out = ET.Element('emultimedia')
    #     for emu in emu_records:
    #         emu_out.append(emu)

    #     if os.path.exists(dest_prefix) == False:
    #         os.makedirs(dest_prefix)

    #     with open(dest_prefix + "emu_prepped.xml", 'wb') as f:
    #         f.write(
    #             ET.tostring(
    #                 emu_out,
    #                 xml_declaration=True,
    #                 encoding='utf-8',
    #                 short_empty_elements=True
    #                 )
    #             )


if __name__ == '__main__':
    main()
