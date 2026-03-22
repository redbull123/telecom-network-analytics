from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from airflow.sdk import dag, task
import pandas as pd


default_args ={
    'owner' : 'airflow',
    'retries' : 2,
    'retry_delay' : timedelta(minutes=5)
}

@dag(
    dag_id='dag_etl',
    default_args=default_args,
    start_date=datetime(2025, 1, 25, 2),
    schedule='@daily'
)
def etl():
    @task
    def extract():
        df = pd.read_json('/opt/airflow/dags/events_20260124_092513.json')
        print(df.head())
        return df
    @task
    def transform(df):
        df.loc[:, 'imsi_hash'] = df['imsi_hash'].str.replace('IMSI_', '')
        print(df.head())
        return df
    @task
    def load(df):
        hook = PostgresHook(postgres_conn_id='Test-dB')
        engine = hook.get_sqlalchemy_engine()
        df.to_sql('events', con=engine, if_exists='replace', index=False)
        print("Data loaded successfully")
    

    e = extract()
    if e:
        t = transform(e)
    if t:
        l = load(t)
    else:
        print("It could not transform the data  because the extract task failed.")

etl_dag = etl()
