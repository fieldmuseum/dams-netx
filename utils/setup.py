'''Utils for general setup, config, and logging'''

import datetime
import logging
import os
import re
import sys
from dotenv import dotenv_values

def get_config_dams_netx(netx_env:str=None):
    '''Load variable from .env, and allow forcing the "NETX_ENV" to "TEST"'''

    config = dotenv_values(".env")
    if not config:
        raise Exception("No .env config file found")

    if netx_env == "TEST":
        config['NETX_ENV'] = "TEST"

    return config

def get_sys_argv(number_of_args:int=2):
    '''Return "live/test" & "date" sys.argv variables standardly across scripts'''

    live_or_test = None
    input_date = None

    if len(sys.argv) > 1:
        live_or_test = sys.argv[1]
        if live_or_test not in ["LIVE", "TEST"]:
            raise Exception("Check 1st command-line arg -- expected 'LIVE' or 'TEST'")

    if len(sys.argv) > 2:
        input_date = sys.argv[2]
        if not re.match(r'^\d{4}\-\d{1,2}\-\d{1,2}$', input_date):
            raise Exception("Check 2nd command-line arg -- expected 'YYYY-M-D' (no lead zeroes)")

    if number_of_args==1:
        return live_or_test
    else:
        return live_or_test, input_date


def get_path_from_env(live_or_test, live_path, test_path):
    '''Return and log a live or test path env variable'''

    if live_or_test == "LIVE":
        path_from_env = live_path  # config('ORIGIN_PATH_XML')
    else:
        path_from_env = test_path  # config('TEST_ORIGIN_PATH_XML')

    # main_xml_input = full_xml_prefix + 'NetX_emultimedia/' + input_date + '/xml*'
    input_path_log = f'Input path = {path_from_env}'
    # print(input_path_log)
    logging.info(input_path_log)

    return path_from_env


def start_log_dams_netx(config:dict=None, log_level=logging.INFO, cmd_args:list=None):
    '''
    Append console output to log-file
    See https://docs.python.org/2/howto/logging.html#logging-to-a-file
    '''

    if config is None:
        config = get_config_dams_netx()

    today = datetime.datetime.today().strftime('%Y%m%d')
    script_to_log = re.sub(r'\.py$', '', sys.argv[0])
    log_file = config['LOG_OUTPUT'] + f'{script_to_log}-{today}.log'

    if cmd_args is None and sys.argv is not None:
        cmd_args = sys.argv
    # else:
    #     raise Exception("Missing 'cmd_args' input for setup.start_log_dams_netx")

    if isinstance(cmd_args, list):
        cmd_args = ' '.join(cmd_args)

    logging.basicConfig(
        filename=log_file,
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S')

    start_time = datetime.datetime.now()
    # logging.info(f'STARTED - {start_time} : {__file__} {cmd_args}')
    logging.info('STARTED - %s : %s %s', start_time, __file__, cmd_args)


def stop_log_dams_netx():
    '''Record finish time and stop logging'''

    stop_time = datetime.datetime.now()
    # logging.info(f'FINISHED {stop_time} : {__file__}')
    logging.info('FINISHED %s : %s', stop_time, __file__)


def get_most_recent_file_in_dir(directory:str) -> str:
    '''Return filepath for most recently modified file in a given dir'''

    max_mod_time = 0
    max_dir = None
    max_file = None

    for dirname,subdirs,files in os.walk(directory):
        for fname in files:
            full_path = os.path.join(dirname, fname)
            mod_time = os.stat(full_path).st_mtime
            if mod_time > max_mod_time:
                max_mod_time = mod_time
                max_dir = dirname
                max_file = fname

    return f'{max_dir}/{max_file}'
