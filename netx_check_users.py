'''Check that users are only in one group via NetX API'''

import ast
import logging
import time
from utils import netx_api as un
from utils import csv_tools as uc
from utils import setup
# from dotenv import dotenv_values


def check_user_groups(group_id:int, live_or_test:str):
    '''For users in a given group, check that each user is only in 1 group & return user-list'''

    # In case API needs rate-limiting
    time.sleep(0.1)

    group_members = un.netx_get_users_by_group(group_id=group_id, netx_env=live_or_test)

    group_user_list = []

    try:

        for member in group_members['result']['results']:

            user_id = member['userId']

            user_groups = un.netx_get_groups_by_user(user_id=user_id, netx_env=live_or_test)

            user_groups_list = user_groups['result']['results']

            if len(user_groups_list) > 0:
                warn_msg = f"WARNING - user ID {user_id} is in multiple groups"
                print(warn_msg)
                logging.warning(warn_msg)

            else:
                log_message = f'{user_id} - in single group {user_groups_list}'
                logging.info(log_message)

            user_group_names = []
            user_group_ids = []
            for group in user_groups_list:
                group_name = group['name']
                group_id = str(group['groupId'])
                user_group_names.append(group_name)
                user_group_ids.append(group_id)

            user_row = {
                'user_id':user_id,
                'group_count': len(user_groups_list),
                'user_group_name': ' | '.join(user_group_names),
                'user_group_id': ' | '.join(user_group_ids)
            }

            group_user_list.append(user_row)

        return group_user_list

    except KeyError as err:
        log_err = f'ERROR - {err}'
        print(log_err)
        logging.error(log_err)


def main():
    '''main function'''

    setup.start_log_dams_netx(config=None)

    live_or_test = setup.get_sys_argv(1)

    config = setup.get_config_dams_netx(live_or_test)

    if live_or_test == 'LIVE':
        group_list = ast.literal_eval(config['NETX_GROUP_IDS'])
    else:
        group_list = ast.literal_eval(config['TEST_NETX_GROUP_IDS'])

    user_checklist = []

    for group_id in group_list:
        print(f'group ids {group_id}')

        group_members = check_user_groups(group_id=group_id, live_or_test=live_or_test)

        if group_members is not None and len(group_members) > 0:
            for row in group_members:
                if row not in user_checklist:
                    user_checklist.append(row)
    
    if len(user_checklist) > 0:
        field_names = []
        for row in user_checklist:
            keys = row.keys()
            for key in keys:
                if key not in field_names:
                    field_names.append(key)

        uc.write_list_of_dict_to_csv(
            input_records=user_checklist,
            field_names=field_names,
            output_csv_file_name=f"{config['LOG_OUTPUT']}/user_checklist.csv"
        )


    setup.stop_log_dams_netx()


if __name__ == '__main__':
    main()
