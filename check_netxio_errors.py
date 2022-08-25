'''Check NetXIO lostandfound and sync.log errors'''

from fileinput import filename
import hashlib, logging, os, re, shutil
import utils.setup as setup
import utils.netx_api as netx_api


def list_files(directory:str):
    '''get a list of files with full filepaths in a directory (recursive)'''

    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_name = file
            file_path = os.path.join(root, file)
            file_row = {
                'name':file_name,
                'path':file_path,
                'path_root':root
            }
            paths.append(file_row)

    return paths


def main():
    '''Main function'''

    setup.start_log_dams_netx()

    config = setup.get_config_dams_netx()
    lost_and_found_files = list_files(config['NETXIO_LOSTANDFOUND']) 


    # check for trailing slash in NetXIO source dir value
    netxio_source_dir = config['NETXIO_LOCAL_SOURCE_DIR']
    if re.match(r'.*/$', netxio_source_dir) is None:
        netxio_source_dir += '/'


    # Check each lost-&-found file
    for file_row in lost_and_found_files:

        file_name = file_row['name']
        file_path = file_row['path']
        file_root = file_row['path_root']


        # Check if file is in NetX
        # - by filename
        asset_data = netx_api.netx_get_asset_by_filename(file_name)

        if 'result' in asset_data and len(asset_data['result']['results']) > 0:

            asset_id = asset_data['result']['results'][0]['id']
            os.remove(file_path)

            log_message= f'{file_name} is NetX asset {asset_id}  | removed from lostandfound'
            print(log_message)
            logging.info(log_message)

        else:
            
            # - by checksum
            # - - get md5 of lost-found-file
            
            with open(file_path,'rb') as f:
                bytes = f.read()
                file_md5 = hashlib.md5(bytes).hexdigest()

            asset_data_md5 = netx_api.netx_get_asset_by_field("fileChecksum", file_md5)

            # Get NetX Asset ID by md5
            if 'result' in asset_data_md5 and len(asset_data_md5['result']['results']) < 1:

                file_path_edit = re.sub(config['NETXIO_LOSTANDFOUND'] ,'', file_path)
                file_path_edit = re.sub(file_name ,'', file_path_edit)

                log_message = f'no NetX match for {file_name} / md5 {file_md5} - moving file for NetXIO back to: {netxio_source_dir + file_path_edit}'
                print(log_message)
                logging.error(log_message)

                if os.path.exists(netxio_source_dir + file_path_edit) == False:
                    os.makedirs(netxio_source_dir + file_path_edit)

                shutil.move(file_path, netxio_source_dir + file_path_edit)

            else:

                asset_id = asset_data['result']['results'][0]['id']
                os.remove(file_path)

                log_message= f'{file_name} (md5 = {file_md5}) is NetX asset {asset_id} | removed from lostandfound'
                print(log_message)
                logging.info(log_message)
                        
    setup.stop_log_dams_netx()


if __name__ == '__main__':
  main()
