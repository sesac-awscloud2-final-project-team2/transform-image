'''배포용
파이썬 실행 시 모듈 동작.
table 이름, 진행 건수를 받으면 해당 테이블의 진행 로그 데이터 확인 후 순차 진행.
진행할 내용 없으면 중단.
'''

import argparse  # argparse 모듈 추가
from modules.load_dynamodb import get_dynamo_data
from modules.update_elt_state import ETLStateController
from modules.transform_to_rds import load_insert_function

from modules.custom_log.custom_logger import CustomLogger
logger = CustomLogger('transform')

from modules.custom_log.prometheus_logger import PrometheusLogger
pm_logger = PrometheusLogger('transform')

# 인자 파서 설정
parser = argparse.ArgumentParser(description='ETL 프로세스 실행')
parser.add_argument('--table_name', type=str, required=True)
parser.add_argument('--batch', type=int, nargs='?', default=10, help='진행 건수 (기본값: 1)')  # 기본값 1

args = parser.parse_args()  # 인자 파싱

table_name = args.table_name
batch = int(args.batch)

etl_state_ctl = ETLStateController(table_name)
start_id = etl_state_ctl.start_etl_state(batch)

code = start_id[0]
id_start_num = int(start_id[1:])
id_end_num = id_start_num+batch
fail_cnt = 0

for id_num in range(id_start_num, id_end_num):
    idx = code + str(id_num)
    prome_label = f'Transform_{table_name}_{idx}'

    data_dict = get_dynamo_data(table_name, idx)
    if len(data_dict) == 0:
        etl_state_ctl.insert_fail_state("get_dynamo_data", idx)
        fail_cnt += 1
        pass
    
    try:
        insert_func = load_insert_function(table_name)
        insert_func(data_dict)
    except Exception as e:
        logger.error('__run__.insert_function', f'No saving data : {prome_label}', e)
        pm_logger.error('__run__.insert_function')
        etl_state_ctl.insert_fail_state("load_insert_function", idx)
        continue

# if fail_cnt == 0:
etl_state_ctl.update_etl_state(start_id, idx, 'finished')
# else:
#     etl_state_ctl.update_etl_state(start_id, idx, 'check needed')