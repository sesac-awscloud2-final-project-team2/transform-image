from airflow import DAG
from datetime import datetime
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

import os
from dotenv import load_dotenv
load_dotenv("dags/.env")
TAG_VERSION = os.getenv('TAG_VERSION')

default_args = {
   'owner': 'aws',
   'depends_on_past': False,
   'start_date': datetime(2025, 2, 10),
   'provide_context': True
}

#use a kube_config stored in s3 dags folder for now
kube_config_path = '/usr/local/airflow/dags/kube_config.yaml'

def get_running_pod(table_name, batch=10):
   PodRun = KubernetesPodOperator(
                        namespace="mwaa",
                        image=f"390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:{TAG_VERSION}",
                        cmds=["/bin/bash", "-c"],
                        arguments=["python __run__.py --table_name={{ params.table_name }} --batch={{ params.batch }}"],
                        labels={"role": "transform"}, # k8s 식별용 라벨
                        name=f"transform-{table_name}",
                        task_id=f"transform-{table_name}",
                        get_logs=True,
                        dag=dag,
                        is_delete_operator_pod=False,
                        config_file=kube_config_path,
                        in_cluster=False,
                        cluster_context='aws',
                        params={
                              'batch': batch,
                              'table_name': table_name
                           }
                        )
   return PodRun

with DAG('transform_dynamo_to_rds', default_args=default_args, schedule_interval=None) as dag:
   joinPodRun = get_running_pod('user')