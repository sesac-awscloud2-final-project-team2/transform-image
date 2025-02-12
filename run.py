'''
파이썬 실행 시 모듈 동작.
table 이름, 진행 건수를 받으면 해당 테이블의 진행 로그 데이터 확인 후 순차 진행.
진행할 내용 없으면 중단.
'''

import argparse  # argparse 모듈 추가
from load_dynamodb import get_dynamo_data
from update_elt_state import ETLStateController
from transform_data import load_insert_function

# 인자 파서 설정
parser = argparse.ArgumentParser(description='ETL 프로세스 실행')
parser.add_argument('batch_count', type=int, nargs='?', default=1, help='진행 건수 (기본값: 1)')  # 기본값 1

args = parser.parse_args()  # 인자 파싱

tables = ['user', 'trip', 'experience']
batch = int(args.batch_count)

for table_name in tables:
    etl_state_ctl = ETLStateController(table_name)
    start_id = etl_state_ctl.start_etl_state(batch)

    code = start_id[0]
    id_start_num = int(start_id[1:])
    id_end_num = id_start_num+batch

    for id_num in range(id_start_num, id_end_num):
        idx = code + str(id_num)
        data_dict = get_dynamo_data(table_name, idx)

        if len(data_dict) == 0:
            break
        
        try:
            insert_func = load_insert_function(table_name)
            insert_func(data_dict)
        except Exception as e:
            etl_state_ctl.insert_fail_state("load_insert_function", idx)
            continue

    etl_state_ctl.update_etl_state(start_id, idx, 'finished')