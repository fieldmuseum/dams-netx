'''Utils for moving, renaming, and handling media files'''

import os
import re
from pygltflib import GLTF2, BufferFormat
from paramiko import SSHClient
from scp import SCPClient
from utils import csv_tools as ct
from utils import setup

# convert gltf to glb
def gltf_bin_to_glb(in_gltf:str='',
                    has_buffer:bool=True,
                    to_binary:bool=False,
                    out_file:str='test.glb'
                    ):
    '''convert a 3d GLTF file with associated BIN (buffer) file to GLB format'''

    original = GLTF2().load(in_gltf)

    # If any buffer URIs (e.g. external '.bin' files), convert them to data.
    if has_buffer is True:
        if to_binary is True:
            original.convert_buffers(BufferFormat.BINARYBLOB)
            original.save_binary(out_file)

        else:
            original.convert_buffers(BufferFormat.DATAURI)
            original.save(out_file)

    else:
        original.save(out_file)


# def validate_gltf(file:str=''):
#     '''validate GLTF file using pygltflib'''


def rename_files_in_list(names_list_csv:str='', from_name_list:list=None):
    '''
    rename a list of files (strings) to a corresponding set of names from a CSV
    names_list_csv: filepath to a CSV (as a string). The CSV should contain 2 columns:
        - from_name = an existing badly-named file (including file extension)
        - to_name = the new name that file should have (including file extension)
    from_name_list: the list of raw file-names that need to be renamed
    '''
    names_list = ct.rows(names_list_csv)
    from_name_list = [row['from_name'] for row in names_list]
    to_name_list = [row['to_name'] for row in names_list]

    # import list of from-names and to-names
    for from_name in from_name_list:
        from_name_clean = re.sub(r'(.+\\/)+', '', from_name)

        # rename files
        if from_name_clean in from_name_list:
            from_index = from_name_list.index(from_name_clean)
            to_name = to_name_list[from_index]
            os.rename(from_name, to_name)


def copy_files_in_list(paths_list:list=None, from_path_prefix:str='', env:str='TEST'):
    '''
    Copy a list of files (strings) to a corresponding set of paths in a new location

    paths_list_csv: filepath to a CSV (as a string). The CSV should contain 2 columns:
        - from_path = path where a file will be pulled from
        - to_path = the new path where a file should go
    
    env: set this to 'LIVE' or 'TEST' to copy to a live or test server 
    
    REMOVED--from_path_list: the list of paths + files that need to be moved
    '''
    config = setup.get_config_dams_netx()
    login_id = config['LOGIN_USERNAME']
    login_pw = config['LOGIN_PASSWORD']
    if env == 'LIVE':
        server = config['HOST']
        # dir_path = config['ORIGIN_PATH_MEDIA']
        dir_path = config['ORIGIN_MEDIA_BASE_DIR']
    else:
        server = config['TEST_HOST']
        dir_path = config['ALT_MEDIA_BASE_DIR']

    if paths_list is None:
        paths_list = []

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=server, username=login_id, password=login_pw)
    # ssh.connect(f'{login_id}@{server}:{dir_path}', password=login_pw)

    # paths_list = ct.rows(paths_list_csv)
    # from_path_list = [row['from_path'] for row in paths_list]
    # to_path_list = [row['to_path'] for row in paths_list]

    with SCPClient(ssh.get_transport()) as scp:
        # import list of from-names and to-names

        missing = []

        i = 0

        for row in paths_list:
            i += 1
            if os.path.exists(f"{from_path_prefix}{row['from_path']}"):
                print(f"{i}/{len(paths_list)} : moving {from_path_prefix}{row['from_path']} to {dir_path}{row['to_path']}")
                scp.put(files = f"{from_path_prefix}{row['from_path']}",
                        remote_path = f"{dir_path}{row['to_path']}",
                        recursive = True)
            else:
                print(f"{i}/{len(paths_list)} : MISSING FILE: {from_path_prefix}{row['from_path']}")
                missing.append(row)

    # output errors:
    if len(missing) > 0:
        print(f"Writing {len(missing)} missing files to 'missing_files.csv'")
        ct.write_list_of_dict_to_csv(input_records=missing, 
                                     field_names=missing[0].keys(),
                                     output_csv_file_name= 'missing_files.csv')
