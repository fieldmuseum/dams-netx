'''
Check which files actually exist on EMu server
e.g. - to narrow down which MM records' Res/Doc tabs need updates on front end
NOTE 
- 'updates' = user manually runs 'update resource' on the frontend in an MM record.
    --> That MM record's Resolutions and/or Documents tab refreshes accurately.
- JPG-thumbnails for PDFs can be batch-prepped in Bridge
'''

import re
import utils.media_tools as um
import utils.csv_tools as uc

def main():
    '''main function'''

    # # Report from EMu:
    # 1. Multimedia records -- e.g. format = pdf ,  subjects = RFG  &  publish = Yes
    # 2. Report = "irn MulIdentifier AccessURI"
    # 3. Rename "emultime.csv" --> "filename_list.csv"

    # Import CSV
    filenames = uc.rows('testing/filename_list_TEST.csv')

    # # test on subset:
    # filenames = filenames[:3]

    # Check which files (main + resolution/docs) actually exist on Shackleton
    dirs, missing = um.check_files_in_list(filename_list=filenames,
                                           env='TEST')

    # output errors:
    if len(missing) > 0:
        print(f"Writing {len(missing)} missing directories to 'missing_dirs.csv'")
        uc.write_list_of_dict_to_csv(input_records=missing,
                                     field_names=missing[0].keys(),
                                     output_csv_file_name= 'missing_dirs.csv')


    # output directory contents table:
    if len(dirs) == 0:
        print("No directory contents to output; check env vars")

    else:

        for directory in dirs:
            directory['PDF'] = ''
            directory['JPG'] = ''
            directory['thumbs_or_600'] = ''

            for filename in directory['dir_filenames']:

                # Check whether PDF records
                pdf = re.findall(r'\S+\.pdf',filename)
                if len(pdf) > 0:
                    directory['PDF'] += f'|{pdf[0]}'

                # - include a JPG?
                jpg = re.findall(r'\S+\.jpe*g',filename)
                if len(jpg) > 0:
                    directory['JPG'] += f'|{jpg[0]}'

                # - and if so, does JPG's name [-extension] match PDF's name?

                # - include thumb/600x600 jpg?
                thumbs = re.findall(r'\S+\.(thumb|600x600)\.jpe*g',
                                    filename)
                if len(jpg) > 0:
                    directory['thumbs_or_600'] += f'|{thumbs[0]}'


        print(f"Writing {len(dirs)} rows to 'dir_contents.csv'")
        uc.write_list_of_dict_to_csv(input_records=dirs,
                                     field_names=dirs[0].keys(),
                                     output_csv_file_name= 'dir_contents.csv')


if __name__ == "__main__":
    main()
