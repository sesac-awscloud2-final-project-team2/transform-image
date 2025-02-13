'''
파이썬 실행 시 모듈 동작.
table 이름, 진행 건수를 받으면 해당 테이블의 진행 로그 데이터 확인 후 순차 진행.
진행할 내용 없으면 중단.
'''

import argparse  # argparse 모듈 추가
from load_dynamodb import get_dynamo_data
from update_elt_state import ETLStateController
from transform_data import load_insert_function
from prometheus_client import Counter, Histogram
import time

# 인자 파서 설정
parser = argparse.ArgumentParser(description='ETL 프로세스 실행')
parser.add_argument('table_name', type=str, required=True)
parser.add_argument('batch', type=int, nargs='?', default=10, help='진행 건수 (기본값: 1)')  # 기본값 1

args = parser.parse_args()  # 인자 파싱

table_name = args.table_name
batch = int(args.batch)


# 요청 횟수를 측정하는 Counter 정의
request_counter = Counter(
    'by_path_counter', 'Request count by request paths',
    ['path']
)

# 요청 처리 시간을 측정하는 Histogram 정의
request_duration = Histogram(
    'http_request_duration_seconds', 'Request processing time',
    ['path']
)


# for table_name in tables:
etl_state_ctl = ETLStateController(table_name)
start_id = etl_state_ctl.start_etl_state(batch)

code = start_id[0]
id_start_num = int(start_id[1:])
id_end_num = id_start_num+batch

for id_num in range(id_start_num, id_end_num):
    idx = code + str(id_num)
    prome_label = f'Transform_{table_name}_{idx}'

    start_time = time.time()
    data_dict = get_dynamo_data(table_name, idx)
    request_duration.labels(prome_label+'_get-data').observe(time.time() - start_time) 
    if len(data_dict) == 0:
        pass
    
    try:
        start_time = time.time()
        insert_func = load_insert_function(table_name)
        insert_func(data_dict)
        request_duration.labels(prome_label+'_insert-data').observe(time.time() - start_time) 
        request_counter.labels(prome_label).inc()
    except Exception as e:
        etl_state_ctl.insert_fail_state("load_insert_function", idx)
        continue

etl_state_ctl.update_etl_state(start_id, idx, 'finished')