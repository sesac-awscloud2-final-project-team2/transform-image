'''
trip으로 저장된 trip 데이터를 불러와서 rdb로 저장
'''


from modules.rds_manager import RDSManager

from modules.__config__ import DB_ID, DB_SECRET_NAME
from modules.__config__ import TRIP_COLS

def insert_trip_log(trip_dict):
    table_name = 'travel'
    trip_dict['experience_ids'] = ''
    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=True)
    with rds_manager:
        rds_manager.insert_data(TRIP_COLS, trip_dict, table_name)