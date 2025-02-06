'''
trip으로 저장된 trip 데이터를 불러와서 rdb로 저장
'''
from rds_manager import RDSManager
from utils import load_json, get_secret
secrets = get_secret()
DB_ID = secrets['DB_ID']
DB_SECRET_NAME = secrets['DB_SECRET_NAME']

TRIP_COLS = load_json('db-table-columns/travel.json')

def insert_trip_log(trip_dict):
    table_name = 'travel'
    trip_dict['experience_ids'] = ''
    rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=False)
    with rds_manager:
        rds_manager.insert_data(TRIP_COLS, trip_dict, table_name)
