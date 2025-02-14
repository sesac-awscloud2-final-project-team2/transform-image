"""
rds 불러오고 종료하는 클래스
"""
import boto3
import json
from botocore.exceptions import ClientError
import psycopg2

from modules.custom_log.custom_logger import CustomLogger, time
logger = CustomLogger('transform')

from modules.custom_log.prometheus_logger import PrometheusLogger
pm_logger = PrometheusLogger('transform')

class RDSManager:
    def __init__(self, db_id, secret_name, is_proxy:bool=True, region_name="ap-northeast-2", db_name=''):
        self.session = boto3.session.Session()
        self.region_name = region_name
        self.db_id = db_id
        self.secret_name = secret_name
        self.is_proxy = is_proxy
        self.db_name = db_name

    def get_rds_info(self) -> dict:
        start_time = time.time()
        rds_client = self.session.client('rds', region_name=self.region_name)
        response = rds_client.describe_db_instances()
        logger.boto_call('get_rds_info', 'rds', response['ResponseMetadata']['HTTPStatusCode'], time.time()-start_time)
        pm_logger.boto_call('get_rds_info', 'rds', response['ResponseMetadata']['HTTPStatusCode'], time.time()-start_time)

        info_dict = {}
        if response['DBInstances']:
            instances = response['DBInstances']
            for db_instance in instances:
                if db_instance['DBInstanceIdentifier'] == self.db_id:
                    info_dict['db_host'] = db_instance['Endpoint']['Address']
                    info_dict['port'] = db_instance['Endpoint']['Port']
                    info_dict['db_name'] = db_instance['DBName'] if self.db_name == '' else self.db_name
        else:
            logger.error('get_rds_info', 'No DBInstances', str(e))
            pm_logger.error('get_rds_info')

        return info_dict

    def get_rds_secret(self) -> dict:
        start_time = time.time()
        client = self.session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )

        try:
            response = client.get_secret_value(
                SecretId=self.secret_name
            )
            if 'SecretString' in response:
                secret = response['SecretString']
            else:
                secret = response['SecretBinary'].decode('utf-8')
            secret_dict = json.loads(secret)
            logger.boto_call('get_rds_secret', 'secrets manager', response['ResponseMetadata']['HTTPStatusCode'], time.time()-start_time)
            pm_logger.boto_call('get_rds_secret', 'secrets manager', response['ResponseMetadata']['HTTPStatusCode'], time.time()-start_time)
            return secret_dict
        except ClientError as e:
            logger.error('get_rds_secret', "Can't call secrets.", str(e))
            pm_logger.error('get_rds_secret')
            raise e

    def __enter__(self):
        self.connection = self.get_db_connection()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if exc_type:
        #     print(f"Exception type: {exc_type}")
        #     print(f"Exception value: {exc_val}")
        #     print(f"Traceback: {exc_tb}")a
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def get_db_connection(self):
        secrets = self.get_rds_secret()
        db_info = self.get_rds_info()

        DB_NAME = db_info['db_name']
        DB_PORT = db_info['port']
        DB_USER = secrets['username']
        DB_PASSWORD = secrets['password']
        DB_HOST = db_info['db_host']
        if self.is_proxy:
            insert_num = len(self.db_id) + 1
            DB_HOST = self.db_id + '.proxy-' + DB_HOST[insert_num:]
            
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

    def execute_query(self, query: str, values):
        self.cursor.execute(query, values)

        try: 
            result = self.cursor.fetchall()
        except Exception as e:
            result = None
        return result

    def call_insert_query(self, table_name, columns):
        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        """
        return insert_query

    def insert_data(self, insert_cols, insert_dict, table_name):
        start_time = time.time()
        insert_query = self.call_insert_query(table_name, insert_cols)
        insert_values = [insert_dict.get(column) for column in insert_cols]
        self.execute_query(insert_query, insert_values)
        logger.rds_operation('insert_data', 'insert', f'{self.db_name}-{table_name}', json.dumps(insert_cols), start_time)
        pm_logger.db_operation('insert', f'{self.db_name}-{table_name}', time.time()-start_time)

    def call_update_query(self, table_name, columns, filter_col, filter_val):
        set_clause = ', '.join([f"{col} = %s" for col in columns])
        update_query = f"""
        UPDATE {table_name}
        SET {set_clause}
        WHERE {filter_col} = '{filter_val}'
        """
        return update_query

    def update_data(self, update_cols, update_dict, filter_col, filter_val, table_name):
        start_time = time.time()
        insert_query = self.call_update_query(table_name, update_cols, filter_col, filter_val)
        insert_values = [update_dict.get(column) for column in update_cols]
        self.execute_query(insert_query, insert_values)
        logger.rds_operation('update_data', 'update', f'{self.db_name}-{table_name}', insert_query, start_time)
        pm_logger.db_operation('update', f'{self.db_name}-{table_name}', time.time()-start_time)

    def call_select_last_id_query(self, table_name, id_col, contain_status=False):
        if contain_status:
            select_query = f"""
            SELECT {id_col}, status
            FROM {table_name} 
            ORDER BY CAST(SUBSTRING({id_col} FROM 2) AS INTEGER) DESC 
            LIMIT 1
            """
        else:
            select_query = f"""
            SELECT {id_col}
            FROM {table_name} 
            ORDER BY CAST(SUBSTRING({id_col} FROM 2) AS INTEGER) DESC 
            LIMIT 1
            """
        return select_query
    
    def select_last_id(self, id_col, table_name, is_status=False):
        start_time = time.time()
        id_query = self.call_select_last_id_query(table_name, id_col, is_status)
        result = self.execute_query(id_query, ())
        logger.rds_operation('select_last_id', 'select', f'{self.db_name}-{table_name}', json.dumps(id_col), start_time)
        pm_logger.db_operation('select', f'{self.db_name}-{table_name}', time.time()-start_time)

        if len(result) == 0:    
            last_id = None
            status = None
        else:
            last_id = result[0][0]
            status = result[0][1]
        return last_id, status
    
    def call_select_filter_query(self, table_name, filter_col, filter_val, select_col):
        if select_col == '':
            select_col = filter_col
        select_query = f"""
        SELECT {select_col}
        FROM {table_name}
        WHERE {filter_col} = '{filter_val}'
        """
        return select_query

    def select_filter(self, table_name, filter_col, filter_val, select_col = ''):
        start_time = time.time()
        filter_query = self.call_select_filter_query(table_name, filter_col, filter_val, select_col)
        filter_result = self.execute_query(filter_query, ())
        logger.rds_operation('select_filter', 'select', f'{self.db_name}-{table_name}', f'{json.dumps(filter_col)}-{json.dumps(filter_val)}', start_time)
        pm_logger.db_operation('select', f'{self.db_name}-{table_name}', time.time()-start_time)
        return filter_result
