#  trans_data_type : ['user', 'trip', 'experience']

LOG_COLS = ['start_id', 'end_id', 'status']
DB_NAME = 'loggingdb'

from rds_manager import RDSManager
from utils import get_secret

secrets = get_secret()
DB_ID = secrets['DB_ID']
DB_SECRET_NAME = secrets['DB_SECRET_NAME']

class ETLStateController:
    def __init__(self, raw_table_name, is_proxy=False) -> None:
        self.raw_table_name = raw_table_name
        self.table_name = 'save_log_'+raw_table_name
        self.rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=is_proxy, db_name=DB_NAME)
    
    def load_last_end_id(self):
        with self.rds_manager:
            last_end_id = self.rds_manager.select_last_id('end_id', self.table_name)
        return last_end_id
    
    def start_etl_state(self, batch=100):
        last_end_id = self.load_last_end_id()
        if last_end_id == None:
            last_end_id = self.raw_table_name[0] + '0'
        start_id = last_end_id[0] + str(int(last_end_id[1:])+1)
        insert_dict = {
            "start_id": start_id,
            "end_id": start_id[0] + str(int(start_id[1:])-1+batch),
            "status": "start"
        }
        with self.rds_manager:
            self.rds_manager.insert_data(LOG_COLS, insert_dict, self.table_name)
        print(insert_dict)
        return start_id

    def update_etl_state(self, start_id, end_id, status):
        update_dict = {
            'end_id':end_id,
            'status':status
        }
        with self.rds_manager:
            self.rds_manager.update_data(update_dict.keys(), update_dict, 'start_id', start_id, self.table_name)
        update_dict['start_id'] = start_id
        print(update_dict)

    def insert_fail_state(self, fail_id):
        fail_info_dict = {
            'start_id':fail_id,
            'end_id':fail_id,
            'status':'fail'
        }
        with self.rds_manager:
            self.rds_manager.insert_data(LOG_COLS, fail_info_dict, self.table_name)
            print(fail_info_dict)