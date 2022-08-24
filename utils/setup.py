'''Utils for general setup, config, and logging'''

import datetime, logging, sys
from dotenv import dotenv_values

def get_config_dams_netx():

    config = dotenv_values(".env")
    if not config: raise Exception("No .env config file found")

    return config


def start_log_dams_netx(config:dict, log_level=logging.INFO, cmd_args:list=sys.argv):
    '''
    Append console output to log-file
    See https://docs.python.org/2/howto/logging.html#logging-to-a-file
    '''
    
    if config is None:
        config = get_config_dams_netx()

    today = datetime.datetime.today().strftime('%Y%m%d')
    log_file = config['LOG_OUTPUT'] + f'dams-netx-{today}.log'

    if type(cmd_args) == list:
        cmd_args = ' '.join(cmd_args)

    logging.basicConfig(
        filename=log_file, 
        level=log_level, 
        format='%(asctime)s %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p')

    start_time = datetime.datetime.now()
    logging.info(f'{start_time} - Started : {__file__} {cmd_args}')
    
    
def stop_log_dams_netx():
    '''Record finish time and stop logging'''

    stop_time = datetime.datetime.now()
    logging.info(f'{stop_time} - Stopped - {__file__}')