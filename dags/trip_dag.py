"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from airflow import DAG
from datetime import datetime
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

import os
from dotenv import load_dotenv
load_dotenv("dags/tag_version")
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

with DAG('dynamo_to_rds_trip', default_args=default_args, schedule_interval=None) as dag:
   tripPodRun = get_running_pod('trip')