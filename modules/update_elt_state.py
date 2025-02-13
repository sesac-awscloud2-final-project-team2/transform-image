#  trans_data_type : ['user', 'trip', 'experience']

LOG_COLS = ['start_id', 'end_id', 'status', 'created_at', 'updated_at']
DB_NAME = 'loggingdb'

from modules.custom_log.custom_logger import CustomLogger
logger = CustomLogger('transform')

from modules.rds_manager import RDSManager
from modules.utils import get_secret, get_current_datetime

secrets = get_secret()
DB_ID = secrets['DB_ID']
DB_SECRET_NAME = secrets['DB_SECRET_NAME']

class ETLStateController:
    def __init__(self, raw_table_name, is_proxy=True) -> None:
        self.raw_table_name = raw_table_name
        self.table_name = 'save_log_'+raw_table_name
        self.rds_manager = RDSManager(DB_ID, DB_SECRET_NAME, is_proxy=is_proxy, db_name=DB_NAME)
    
    def load_last_end_id(self):
        with self.rds_manager:
            last_end_id = self.rds_manager.select_last_id('end_id', self.table_name)
        return last_end_id
    
    def start_etl_state(self, batch=100):
        start_time = logger.start('start_etl_state')
        last_end_id = self.load_last_end_id()
        if last_end_id == None:
            last_end_id = self.raw_table_name[0] + '0'
        start_id = last_end_id[0] + str(int(last_end_id[1:])+1)
        insert_dict = {
            "start_id": start_id,
            "end_id": start_id[0] + str(int(start_id[1:])-1+batch),
            "status": "start",
            "created_at": get_current_datetime()
        }
        with self.rds_manager:
            self.rds_manager.insert_data(LOG_COLS, insert_dict, self.table_name)
        logger.rds_operation("start_etl_state", 'insert', self.table_name, 1, start_time)
        logger.finish('start_etl_state')
        return start_id

    def update_etl_state(self, start_id, end_id, status):
        start_time = logger.start('update_etl_state')
        update_dict = {
            'end_id':end_id,
            'status':status,
            'updated_at': get_current_datetime()
        }
        with self.rds_manager:
            self.rds_manager.update_data(update_dict.keys(), update_dict, 'start_id', start_id, self.table_name)
        update_dict['start_id'] = start_id
        logger.rds_operation("update_etl_state", 'update', self.table_name, 1, start_time)
        logger.finish('update_etl_state')

    def insert_fail_state(self, func_name, fail_id):
        start_time = logger.start('insert_fail_state')
        fail_info_dict = {
            'func_name':func_name,
            'start_id':fail_id,
            'end_id':fail_id,
            'status':'fail',
            'updated_at': get_current_datetime()
        }
        with self.rds_manager:
            self.rds_manager.insert_data(LOG_COLS, fail_info_dict, self.table_name)
        logger.rds_operation('insert_fail_state', 'insert', self.table_name, 1, start_time)
        logger.finish('insert_fail_state')

