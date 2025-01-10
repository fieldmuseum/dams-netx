'''
dams-netx task list
'''

from datetime import datetime
import logging
import os
import time
import prep_emu_media
import check_netxio_errors
import prep_emu_xml
import prep_pathadd
import netx_add_folder
import netx_remove_asset
import netx_update_collections
import netx_remove_collection
from utils import setup


def main():
    '''Run through dams-netx sync tasks'''

    today = str(datetime.today())[:10]
    prep_live_or_test = 'LIVE'
    netx_live_or_test = 'LIVE'

    # Start logs
    setup.start_log_dams_netx(config=None, cmd_args=[prep_live_or_test, today])

    config = setup.get_config_dams_netx(prep_live_or_test)


    # # # # Start dams-netx steps:

    # 1 - Prep media files
    logging.info(' - - prep_emu_media - %s - %s - - -', prep_live_or_test, today)
    prep_emu_media.main(live_or_test=prep_live_or_test, input_date=today)


    # 2 - Run NetXIO to ingest media files
    if netx_live_or_test == 'LIVE':
        netx_io_props = config['NETXIO_PROPS']
    else:
        netx_io_props = config['TEST_NETXIO_PROPS']
    
    netx_io_jar = config['NETXIO_JAR']
    netx_io =  f'sudo java -Xms512M -Xmx2048M -cp "{netx_io_jar}" com.netxposure.external.client.io.NetxIO -config "{netx_io_props}"'
    logging.info('NETX_IO:  %s', netx_io)
    os.system(netx_io)
    time.sleep(1)


    # 3 - Update folder permissions
    update_folder_permission = "cd /home/kwebbink/NetxIO/NetxIO_workfiles/ && sudo chown -R kwebbink:10513 lostandfound"
    logging.info('Edit Folder permission:  %s', update_folder_permission)
    os.system(update_folder_permission)
    time.sleep(1)


    # 4 - (dams-netx) Check for NetXIO lostandfound
    logging.info(' - - check_netxio_errors - - -')
    check_netxio_errors.main(prep_live_or_test)

    # 5 - (dams-netx) Prep XML for DSS
    logging.info(' - - prep_emu_xml - - -')
    prep_emu_xml.main(prep_live_or_test, today)


    # 6 - (NetXIO) Run NexIO DSS-xml-file import
    if netx_live_or_test == 'LIVE':
        netxio_dss_props = config['NETXIO_DSS_PROPS']
    else:
        netxio_dss_props = config['TEST_NETXIO_DSS_PROPS']

    netx_io_dss = f'sudo java -Xms512M -Xmx2048M -cp "{netx_io_jar}" com.netxposure.external.client.io.NetxIO -config "{netxio_dss_props}"'
    logging.info('NETX_IO_DSS:  %s', netx_io_dss)
    os.system(netx_io_dss)
    time.sleep(1)


    # 7 - (dams-netx) Prep pathAdd folder-update
    logging.info(' - - prep_pathadd - - -')
    prep_pathadd.main(prep_live_or_test, today)

    # 8 - (dams-netx) Update folders via NetX API
    logging.info(' - - netx_add_folder - - -')
    netx_add_folder.main(prep_live_or_test)

    # 9 - (dams-netx) Move unpublished/deleted assets to "Remove_from_NetX" folder
    logging.info(' - - netx_remove_asset - - -')
    netx_remove_asset.main(prep_live_or_test, today)

    # 10 - (dams-netx) Update Groups via NetX API
    logging.info(' - - netx_update_collections - - -')
    netx_update_collections.main(prep_live_or_test, today)

    # 11 (dams-netx) Remove unpublished/deleted collections
    logging.info(' - - netx_remove_collection - - -')
    netx_remove_collection.main(prep_live_or_test, today)


    # Stop logs
    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
