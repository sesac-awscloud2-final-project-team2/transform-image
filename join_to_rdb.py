'''
join으로 저장된 user 데이터를 불러와서 rdb로 저장
'''
from rds import RDSManager

from __config__ import USER_COLS, DB_ID, DB_SECRET_NAME


def insert_join_user(user_dict):
    table_name = 'users'
    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=False)
    with rds_manager:
        rds_manager.insert_data(USER_COLS, user_dict, table_name)