
import json
from datetime import datetime

def load_json(json_fname):
    with open(json_fname, 'r') as f:
        return json.load(f)

def get_current_datetime():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')

# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
import json
from botocore.exceptions import ClientError

def get_secret(): 
    secret_name = "transform_to_rds"
    region_name = "ap-northeast-2"

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
        # Handle known exceptions
        print(f"An error occurred: {e}")
        raise e