
import json
from datetime import datetime

def load_json(json_fname):
    with open(json_fname, 'r') as f:
        return json.load(f)

def get_current_datetime():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
