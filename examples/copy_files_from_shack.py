"""
Example Python script that shows how to copy media files from Shackleton
to the local Lusca server. Uses Fabric:
https://docs.fabfile.org/en/2.7/getting-started.html#transfer-files
https://docs.fabfile.org/en/2.7/api/transfer.html
https://docs.fabfile.org/en/2.7/api/transfer.html#fabric.transfer.Transfer.get
"""

from dotenv import dotenv_values
from fabric import Connection

def main():
    """
    Main function for execution of the script.
    """

    config = dotenv_values('.env')
    if not config: raise FileNotFoundError("Couldn't find .env file")

    with Connection(host=config['SHACK_IP'], user=config['SHACK_USER']) as c:
        c.run('hostname')

        # Copy example file
        try:
            media_file_loc = config['SHACK_MEDIA_BASE_DIR'] + config['SHACK_MEDIA_EXAMPLE_FILE_LOC']
            c.get(remote=media_file_loc, local='examples/media/', preserve_mode=False)
        except Exception as err:
            print(f'An error occurred trying to copy media from Shack to Lusca: {err}')

if __name__ == "__main__":
    main()
