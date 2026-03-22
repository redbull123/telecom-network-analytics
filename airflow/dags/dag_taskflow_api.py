from datetime import datetime, timedelta
from airflow.decorators import dag, task

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

@dag(dag_id='dag_taskflow_api',
     default_args=default_args,
     start_date=datetime(2025, 1, 25, 2)
     ,schedule='@daily')
def etl():
    @task
    def extract():
        data = [1, 2, 3, 4, 5]
        return data
    @task
    def transform(data):
        transformed_data = [x * 2 for x in data]
        return transformed_data
    
    e = extract()
    t = transform(e)
    print(t)
etl_dag = etl()