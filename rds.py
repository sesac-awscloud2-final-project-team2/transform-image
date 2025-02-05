"""
rds 불러오고 종료하는 클래스
"""


import boto3
import json
from botocore.exceptions import ClientError
import psycopg2

class RDSManager:
    def __init__(self, db_id, secret_name, region_name="ap-northeast-2", is_proxy:bool='True'):
        self.session = boto3.session.Session()
        self.region_name = region_name
        self.db_id = db_id
        self.secret_name = secret_name
        self.is_proxy = is_proxy

    def get_rds_info(self) -> dict:
        rds_client = self.session.client('rds')
        response = rds_client.describe_db_instances()
        
        info_dict = {}
        if response['DBInstances']:
            instances = response['DBInstances']
            for db_instance in instances:
                if db_instance['DBInstanceIdentifier'] == self.db_id:
                    break

            info_dict['db_host'] = db_instance['Endpoint']['Address']
            info_dict['port'] = db_instance['Endpoint']['Port']
            info_dict['db_name'] = db_instance['DBName']

        return info_dict

    def get_rds_secret(self) -> dict:
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
            return secret_dict
        except ClientError as e:
            print(f"An error occurred: {e}")
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
        insert_query = self.call_insert_query(table_name, insert_cols)
        insert_values = [insert_dict.get(column) for column in insert_cols]
        self.execute_query(insert_query, insert_values)

    def call_select_last_id_query(self, table_name, id_col):
        select_query = f"""
        SELECT {id_col} 
        FROM {table_name} 
        ORDER BY CAST(SUBSTRING({id_col} FROM 2) AS INTEGER) DESC 
        LIMIT 1
        """
        return select_query
    
    def select_last_id(self, id_col, table_name):
        id_query = self.call_select_last_id_query(table_name, id_col)
        result = self.execute_query(id_query, ())
        if len(result) == 0:
            last_id = None
        else:
            last_id = result[0][0]
        return last_id
    
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
        filter_query = self.call_select_filter_query(table_name, filter_col, filter_val, select_col)
        filter_result = self.execute_query(filter_query, ())
        return filter_result
