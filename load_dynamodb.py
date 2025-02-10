
import boto3
from boto3.dynamodb.conditions import Key

region_name = "ap-northeast-2"

# DynamoDB 클라이언트 생성
dynamodb = boto3.resource(
    'dynamodb',
    region_name=region_name
)

def get_dynamo_data(table_name, idx) -> dict:
    table = dynamodb.Table(table_name)

    response = table.query(
        KeyConditionExpression=Key(f'{table_name}_id').eq(idx),
    )

    items = response['Items']
    if len(items) == 0:
        return {}
    else:
        return items[0]