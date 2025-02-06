#  trans_data_type : ['user', 'trip', 'experience']

LOG_COLS = ['start_id', 'end_id', 'status']
DB_NAME = 'loggingdb'

from rds_manager import RDSManager
from utils import get_secret

secrets = get_secret()
DB_ID = secrets['DB_ID']
DB_SECRET_NAME = secrets['DB_SECRET_NAME']

class ETLStateController:
    def __init__(self, trans_data_type, is_proxy=False) -> None:
        self.trans_data_type = trans_data_type
        self.table_name = 'save_log_'+trans_data_type
        self.rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=is_proxy, db_name=DB_NAME)
    
    def load_last_end_id(self):
        with self.rds_manager:
            last_end_id = self.rds_manager.select_last_id('end_id', self.table_name)
        return last_end_id
    
    def start_etl_state(self, batch=100):
        last_end_id = self.load_last_end_id()
        start_id = last_end_id[0] + str(int(last_end_id[1:])+1)
        insert_dict = {
            "start_id": start_id,
            "end_id": start_id[0] + str(int(start_id[1:])+batch),
            "status": "start"
        }
        with self.rds_manager:
            self.rds_manager.insert_data(LOG_COLS, insert_dict, self.table_name)

    def update_etl_state(self, start_id, end_id, status):
        update_dict = {
            'end_id':end_id,
            'status':status
        }
        with self.rds_manager:
            self.rds_manager.update_data(update_dict.keys(), update_dict, 'start_id', start_id, self.table_name)
