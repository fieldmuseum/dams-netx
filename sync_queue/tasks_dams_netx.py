'''
dams-netx task list
'''

from datetime import datetime
import os
import time
import prep_emu_media
import check_netxio_errors
import prep_emu_xml
import prep_pathadd
import netx_add_folder
import netx_remove_asset
import netx_update_collections
# import netx_create_collection
import netx_remove_collection
# from sync_queue.celery import app

# @app.task
# def add(x:int=0, y:int=1):
#     '''run a test function'''
#     print('x+y')
#     return x + y
# add.apply_async((2, 2), queue='lopri', countdown=10)

# media_prep = prep_emu_media.main.apply_async((today, 'LIVE'), queue='dams-test', countdown=4)
# media_prep.get()

def main():
    '''Run through dams-netx sync tasks'''

    today = str(datetime.today())[:10]
    live_or_test = 'LIVE'


    # 1 - Prep media files
    prep_emu_media.main(live_or_test=live_or_test, input_date=today)


    # 2 - Run NetXIO to ingest media files
    if live_or_test == 'LIVE':
        netx_io =  'sudo java -Xms512M -Xmx2048M -cp "/home/kwebbink/NetxIO/netxio-4.1.15.jar" com.netxposure.external.client.io.NetxIO -config "/home/kwebbink/NetxIO/netxio.properties"'
    else:
        netx_io = 'sudo java -Xms512M -Xmx2048M -cp "/home/kwebbink/NetxIO/netxio-4.1.15.jar" com.netxposure.external.client.io.NetxIO -config "/home/kwebbink/NetxIO/netxio_test.properties"'
    os.system(netx_io)
    time.sleep(1)


    # 3 - Update folder permissions
    update_folder_permission = "cd /home/kwebbink/NetxIO/NetxIO_workfiles/ && sudo chown -R kwebbink:10513 lostandfound"
    os.system(update_folder_permission)
    time.sleep(1)


    # 4 - (dams-netx) Check for NetXIO lostandfound
    check_netxio_errors.main(live_or_test)

    # 5 - (dams-netx) Prep XML for DSS
    prep_emu_xml.main(live_or_test, today)


    # 6 - (NetXIO) Run NexIO DSS-xml-file import
    if live_or_test == 'LIVE':
        netx_io_dss = 'sudo java -Xms512M -Xmx2048M -cp "/home/kwebbink/NetxIO/netxio-4.1.15.jar" com.netxposure.external.client.io.NetxIO -config "/home/kwebbink/NetxIO/netxio_dss.properties"'
    else:
        netx_io_dss = 'sudo java -Xms512M -Xmx2048M -cp "/home/kwebbink/NetxIO/netxio-4.1.15.jar" com.netxposure.external.client.io.NetxIO -config "/home/kwebbink/NetxIO/netxio_dss_test.properties"'
    os.system(netx_io_dss)
    time.sleep(1)


    # 7 - (dams-netx) Prep pathAdd folder-update
    prep_pathadd.main(live_or_test, today)

    # 8 - (dams-netx) Update folders via NetX API
    netx_add_folder.main(live_or_test)

    # 9 - (dams-netx) Move unpublished/deleted assets to "Remove_from_NetX" folder
    netx_remove_asset.main(live_or_test, today)

    # 10 - (dams-netx) Update Groups via NetX API
    netx_update_collections.main(live_or_test, today)

    # 11 (dams-netx) Remove unpublished/deleted collections
    netx_remove_collection.main(live_or_test, today)


if __name__ == '__main__':
    main()

