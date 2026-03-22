from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)}

with DAG(
    dag_id='second_dag',
    default_args=default_args,
    description='My Second DAG',
    start_date=datetime(2025,1,25,2),
    schedule='@daily'
) as dag:
    task1 = BashOperator(
        task_id='print_file',
        bash_command='cat /opt/airflow/dags/events_20260124_092513.json'
    )

    task1