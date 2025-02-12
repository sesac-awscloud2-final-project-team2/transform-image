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
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

TAG_VERSION = ""

default_args = {
   'owner': 'aws',
   'depends_on_past': False,
   'start_date': datetime(2025, 2, 10),
   'provide_context': True
}

dag = DAG(
   'transform_k8s', default_args=default_args, schedule_interval=None)

#use a kube_config stored in s3 dags folder for now
kube_config_path = '/usr/local/airflow/dags/kube_config.yaml'

joinPodRun = KubernetesPodOperator(
                       namespace="mwaa",
                       image=f"transform:aa", #390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:{TAG_VERSION}",
                       cmds=["/bin/bash", "-c"],
                       arguments=["python", "run.py", "join", "10"],
                       labels={"role": "transform"}, # k8s 식별용 라벨
                       name="transform-join",
                       task_id="transform-join",
                       get_logs=True,
                       dag=dag,
                       is_delete_operator_pod=False,
                       config_file=kube_config_path,
                       in_cluster=False,
                       cluster_context='aws'
                       )

tripPodRun = KubernetesPodOperator(
                       namespace="mwaa",
                       image=f"390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:{TAG_VERSION}",
                       cmds=["/bin/bash", "-c"],
                       arguments=["python", "run.py", "trip", "10"],
                       labels={"role": "transform"}, # k8s 식별용 라벨
                       name="transform-trip",
                       task_id="transform-trip",
                       get_logs=True,
                       dag=dag,
                       is_delete_operator_pod=False,
                       config_file=kube_config_path,
                       in_cluster=False,
                       cluster_context='aws'
                       )

experiecnePodRun = KubernetesPodOperator(
                       namespace="mwaa",
                       image=f"390844761387.dkr.ecr.ap-northeast-2.amazonaws.com/transform:{TAG_VERSION}",
                       cmds=["/bin/bash", "-c"],
                       arguments=["python", "run.py", "experience", "10"],
                       labels={"role": "transform"}, # k8s 식별용 라벨
                       name="transform-experiecne",
                       task_id="transform-experience",
                       get_logs=True,
                       dag=dag,
                       is_delete_operator_pod=False,
                       config_file=kube_config_path,
                       in_cluster=False,
                       cluster_context='aws'
                       )

joinPodRun >> tripPodRun >> experiecnePodRun