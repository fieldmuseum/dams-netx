import utils.media_tools as um
import utils.csv_tools as uc

def main():

    # # Import tables:
    # dato_media = uc.rows('Dato_media_full_export-2024012003_all.csv')
    # dato_guides = uc.rows('Dato_full_export-fg_guide-2024-12-04.csv')
    # emu_guides = uc.rows('EMu_thumbs_group1_prep_import2.csv')

    # # TABLE-1: merge dato_media.dato-pdf names to dato-thumbs by fg_guide id
    # # TABLE-2: merge Group1_prep.emu irns to TABLE-1 by pdf names
    # # TABLE-3: from [path + name], to [path + name]

    # # out:
    # # - create list of
    # #     - Shackleton file-path (formed from EMu IRN)
    # #     - from_name (from Dato filenames)
    # #     - to_name (formed from EMu-PDF filename)

    # Import CSV with 
    from_to = uc.rows('from_to_files.csv')

    # test on subset:
    from_to = from_to[0:5]

    # Copy files from local to server
    um.copy_files_in_list(paths_list=from_to, 
                          from_path_prefix='testing/thumb_batch',
                          env='LIVE')


if __name__ == "__main__":
    main()