"""
rds 관련 정보 불러오는 함수 모음
"""


import boto3
import json
from botocore.exceptions import ClientError
import psycopg2


def get_rds_info() -> dict:
    session = boto3.session.Session()
    rds_client = session.client('rds')
    response = rds_client.describe_db_instances()
    
    info_dict = {}

    if response['DBInstances']:
        db_instance = response['DBInstances'][0]
        info_dict['db_host'] = db_instance['Endpoint']['Address']
        info_dict['port'] = db_instance['Endpoint']['Port']
        info_dict['db_name'] = db_instance['DBName']

    return info_dict

def get_rds_secret(
        secret_name = "rds!db-7a81c7ab-2ef8-4764-bcaa-37e3faf410d2",
        region_name = "ap-northeast-2"    
        ) -> dict:

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(
            SecretId=secret_name
        )

        # Check if SecretString is available
        if 'SecretString' in response:
            secret = response['SecretString']
        else:
            # If the secret is stored as binary, decode it
            secret = response['SecretBinary'].decode('utf-8')
        
        # Parse the secret as JSON
        secret_dict = json.loads(secret)
        return secret_dict  # Return as a dictionary
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        print(f"An error occurred: {e}")
        raise e
    secret_dict = json.loads(secret)
    secret = get_secret_value_response['SecretString']
    
    return secret

    # Your code goes here.



# PostgreSQL 연결 함수
def get_db_connection():
    secrets = get_rds_secret()
    db_info = get_rds_info()

    DB_HOST = db_info['db_host']
    DB_NAME = db_info['db_name']
    DB_PORT = db_info['port']
    DB_USER = secrets['username']
    DB_PASSWORD = secrets['password']
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
