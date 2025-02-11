'''
join으로 저장된 user 데이터를 불러와서 rdb로 저장
'''
from transform_data.tfm_logger import CustomLogger
logger = CustomLogger('transform')

from rds_manager import RDSManager
from utils import load_json, get_secret
secrets = get_secret()
DB_ID = secrets['DB_ID']
DB_SECRET_NAME = secrets['DB_SECRET_NAME']

USER_COLS = load_json('db-table-columns/users.json')

def insert_join_user(user_dict):
    table_name = 'users'
    start_time = logger.start('insert_join_user')
    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=False)
    with rds_manager:
        rds_manager.insert_data(USER_COLS, user_dict, table_name)
    logger.rds_operation('insert', table_name, 1, start_time)
    logger.finish('insert_join_user')