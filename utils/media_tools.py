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
    
    env: set this to 'LIVE', 'TEST', or 'WEB' to copy to a live, test or web server 
    
    REMOVED--from_path_list: the list of paths + files that need to be moved
    '''
    config = setup.get_config_dams_netx()
    login_id = config['LOGIN_USERNAME']
    login_pw = config['LOGIN_PASSWORD']
    if env == 'LIVE':
        server = config['HOST']
        # dir_path = config['ORIGIN_PATH_MEDIA']
        dir_path = config['ORIGIN_MEDIA_BASE_DIR']
    elif env == 'WEB':
        server = config['WEB_HOST']
        dir_path = config['ORIGIN_MEDIA_BASE_DIR']
        login_pw = config['WEB_LOGIN_PASSWORD']
    else:
        server = config['TEST_HOST']
        dir_path = config['ALT_MEDIA_BASE_DIR']

    if paths_list is None:
        paths_list = []

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=server, username=login_id, password=login_pw)
    # ssh.connect(f'{login_id}@{server}:{dir_path}', password=login_pw)

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


def prep_paths_from_irns(records:list=None, base_path_new:str=None) -> list:
    '''
    Given a list of AccessURI values, prep emu filepaths.
    Returns a list of prepped paths to a MM record's folder on the server

    :param records: list - list of dictionaries, in which one key is 'irn' for Multimedia irns
    :param base_path_new: str - the server path to the multimedia share (include trailing slash)

    :return: list - original list of dictionaries with new key 'dir_path' for prepped server path

    '''

    if records is None:
        records = []

    prepped_list = []

    for record in records:
        # parse each irn to form its corresponding filepath
        irn = str(record['irn'])
        prepped_dir = f'{irn[0:(len(irn)-3)]}/{irn[(len(irn)-3):len(irn)]}/'
        dir_path = f'{base_path_new}/{prepped_dir}'
        record['dir_path'] = dir_path
        if record not in prepped_list:
            prepped_list.append(record)


    return prepped_list


def check_files_in_list(filename_list:list=None, env:str='TEST'):
    '''
    Copy a list of files (strings) to a corresponding set of paths in a new location

    filename_list_csv: filepath to a CSV (as a string). The CSV should include:
        - irn = a column of Multimedia irn's
        - other columns are options
    
    env: set this to 'LIVE', 'TEST', or 'WEB' to check on a live, test or web server

    :returns: Two objects:
        - directory_contents:
            list - directories and their contents as a list of dictionaries including:
                irn
                directory path
                directory file-contents
        
        - missing
            - a list of rows whose paths were missing from the server

    '''
    config = setup.get_config_dams_netx()
    login_id = config['LOGIN_USERNAME']
    login_pw = config['LOGIN_PASSWORD']
    if env == 'LIVE':
        server = config['HOST']
        # dir_path = config['ORIGIN_PATH_MEDIA']
        dir_path = config['ORIGIN_MEDIA_BASE_DIR']
    elif env == 'WEB':
        server = config['WEB_HOST']
        dir_path = config['ORIGIN_MEDIA_BASE_DIR']
        login_pw = config['WEB_LOGIN_PASSWORD']
    else:
        server = config['TEST_HOST']
        dir_path = config['ALT_MEDIA_BASE_DIR']

    if filename_list is None:
        filename_list = []

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=server, username=login_id, password=login_pw)
    # ssh.connect(f'{login_id}@{server}:{dir_path}', password=login_pw)

    prepped_filepaths = prep_paths_from_irns(records=filename_list,
                                             base_path_new=dir_path)

    directory_contents = []

    missing = []

    sftp = ssh.open_sftp()

    i = 0

    for row in prepped_filepaths:
        i += 1

        # stdin, stdout, stderr = ssh.exec_command(f"ls {row['dir_path']}")
        # print('----------------stdin----------------')
        # print(stdin)
        # print('----------------stdout----------------')
        # print(stdout)
        # print('----------------stderr----------------')
        # print(stderr)

        # print('----------------stdout formatted----------------')
        # for line in stdout:
        #     print('... ' + line.strip('\n'))

        # row['stdin'] = stdin
        # row['stdout'] = stdout
        # row['stderr'] = stderr

        # if os.path.exists(f"{row['dir_path']}"):
        print(f"{i}/{len(prepped_filepaths)} : checking {row['dir_path']}")
        print(f"list of files:  {sftp.listdir_attr(row['dir_path'])}")

        row['dir_contents'] = sftp.listdir_attr(row)

        row['dir_filenames'] = [entry.filename for entry in row['dir_contents']]
        print(row['dir_filenames'])

        if row not in directory_contents:
            directory_contents.append(row)

        # else:
        #     print(f"{i}/{len(prepped_filepaths)} : MISSING DIR: {row['dir_path']}")
        #     missing.append(row)

    return directory_contents, missing
