'''MorphoSource API test'''

import hashlib
import time
# from dotenv import dotenv_values
# import shutil
# import tempfile
# import zipfile
from datetime import datetime
from morphosource import search_objects, search_media
# search_media, DownloadVisibility # , DownloadConfig  # get_media, 
import utils.csv_tools as uc

def calculate_hash(filename):
    '''Calculate the MD5 hash for a given file'''
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(2 ** 20), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    '''Main function to find and download a test-FM MS media file'''

    # config = dotenv_values('.env')

    # download_config = DownloadConfig(
    #     api_key = config['MS_API_KEY'],
    #     use_statement = "Downloading this data to test cross-checking and sync-ing with FMNH EMu",
    #     use_category_other = "admin checks"
    # )

    search_term = "Field Museum"
    print(f"{datetime.now()} : starting search for: {search_term}")
    # results = search_media(search_term)  # , visibility=DownloadVisibility.OPEN)
    results = search_objects(search_term)  # , visibility=DownloadVisibility.OPEN)
    
    print(f"{datetime.now()} : finished search, # of results:")
    print(f"{len(results.items)} results; outputting first 5")
    media_info = []
    if len(results.items) > 0:
        for obj in results.items[0:5]:
            print(f"Object: {obj.id} : {obj.title}")
            time.sleep(1)
            media_record = {}
            media_list = obj.get_media_ary()
            print(f"{len(media_list)} media records; outputting first 5")
            if len(media_list) > 0:
                for media in media_list:
                    time.sleep(1)
                    # # # # TEST / CHECK THIS
                    media_metadata = media.get_file_metadata()
                    media_record = {
                        'obj_id': obj.id,
                        # 'obj_data':obj.data, # specify occ_id
                        'id': media.id,
                        'title': media.title,
                        'data': media.data,
                        'file_metadata': media_metadata.data
                    }
                    media_info.append(media_record)
                    print(f"{datetime.now()} : Retrieving {media.id} {media.title}")

            # path = f"{media.id}.zip"
            # print(f"Downloading {media.id} {media.title} to {path}")

    # fm_media = get_media("000477685")
    # path = f"{fm_media.id}.zip"
    
    # print(" = = = = = = = = ")
    # print(f"Downloading {fm_media.id} {fm_media.title} to {path}")
    # print("Media DATA = = = = = = ")
    # print(fm_media.data)

    # print(" = = = = = = = = ")
    # print("Media METADATA = = = = = = ")
    # metadata = fm_media.get_file_metadata()
    # print(metadata.data)

    # fm_media.download_bundle(path, download_config)

    if len(media_info) > 0:
        uc.write_list_of_dict_to_csv(input_records = media_info, 
                                     field_names = media_info[0].keys(),
                                     output_csv_file_name = "ms_fm_files_check.csv")

if __name__ == '__main__':
    main()
