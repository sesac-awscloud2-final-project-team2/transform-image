
import datetime
import boto3
from boto3.dynamodb.conditions import Key

from modules.custom_log.custom_logger import CustomLogger, time
logger = CustomLogger('transform')

from modules.custom_log.prometheus_logger import PrometheusLogger
pm_logger = PrometheusLogger('transform')

region_name = "ap-northeast-2"

# DynamoDB 클라이언트 생성
dynamodb = boto3.resource(
    'dynamodb',
    region_name=region_name
)

def get_dynamo_data(table_name, idx) -> dict:
    start_time = time.time()
    table = dynamodb.Table(table_name)

    response = table.query(
        KeyConditionExpression=Key(f'{table_name}_id').eq(idx),
    )

    items = response['Items']
    logger.dynamodb_operation('get_dynamo_data', 'select', table_name, idx, start_time)
    duration = time.time() - start_time
    pm_logger.db_operation('select', 'dynamodb', duration)
    if len(items) == 0:
        logger.error('get_dynamo_data', f'No Data idx({idx}) in {table_name}')
        pm_logger.error('get_dynamo_data')
        return {}
    else:
        return items[0]