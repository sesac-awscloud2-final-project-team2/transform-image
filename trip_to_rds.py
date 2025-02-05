'''
trip으로 저장된 trip 데이터를 불러와서 rdb로 저장
'''
from rds import RDSManager

from __config__ import TRIP_COLS, DB_ID, DB_SECRET_NAME

def insert_trip_log(trip_dict):
    table_name = 'travel'
    trip_dict['experience_ids'] = ''
    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=False)
    with rds_manager:
        rds_manager.insert_data(TRIP_COLS, trip_dict, table_name)
