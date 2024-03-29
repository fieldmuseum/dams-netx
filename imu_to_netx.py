'''Copy and Rename Multimedia files for EMu-to-Netx batches'''
import os, re
from imu_api import imu_api
from dotenv import dotenv_values

config = dotenv_values('.env')
if not config: raise Exception("Couldn't find .env file")

try:
    session = imu_api.create_imu_session(
        host = config['HOST'],
        port = config['PORT'],
        username = config['LOGIN_USERNAME'],
        password = config['LOGIN_PASSWORD']
    )
except Exception as e: print(f'Error connecting to EMu: {e}')


# Get a batch of files (including original irn-based filepath)

#   QUESTION: should script get batch as CSV (initial import) or IMu query (periodic updates)?


# For each file in batch:


    # 1. Copy file to NetX folder, based on [EMu fields]


    # 2. Check for filename prefix:
    # 
    #       IF filename-prefix == [irn]_emu: pass
    #       ELIF filename-prefix == [id]_netx:
    #           check if dato has a matching record? (or just pass?)
    #       ELSE: prepend '[irn]_emu' to filename


