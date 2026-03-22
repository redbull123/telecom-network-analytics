from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator

default_args = {
    'owner' : 'airflow',
    'retries' : 2,
    'retry_delay' : timedelta(minutes=5)
}

def postgres_connection_task_query():
    ## Creo la comunicacion a la Base de Datos
    hook = PostgresHook(postgres_conn_id='Test-dB')
# Usar 'with' asegura que la conexión se cierre sola aunque falle el script
    with hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users;")
            records = cursor.fetchall()
            for row in records:
                print(f"Usuario encontrado: {row}")

def postgres_connection_task_create_table(table):
    hook = PostgresHook(postgres_conn_id='Test-dB')
    with hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (id int, name varchar(255));")
    conn.commit()   
    conn.close()
    print(f"Tabla {table} creada exitosamente")

def postgres_connection_task_insert_data():
    hook = PostgresHook(postgres_conn_id='Test-dB')

    with hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (id, name) VALUES (2, 'Airflow User');")
    conn.commit()
    conn.close()
    print("Datos insertados exitosamente")

def postgres_connection_task_delete_data():
    hook =PostgresHook(postgres_conn_id='Test-dB')
    with hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = 2;")
    conn.commit()
    conn.close()
    print("Datos eliminados exitosamente")


with DAG(
    dag_id='dag_connection_to_pg',
    default_args=default_args,
    start_date=datetime(2026,2,25),
    schedule='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='postgres_connection_task',
        python_callable=postgres_connection_task_query
    )

    task2 = PythonOperator(
        task_id='pg_conn_create_table',
        python_callable=postgres_connection_task_create_table,
        op_kwargs={'table': 'test_table'}
    )

    task3 = PythonOperator(
        task_id='pg_conn_insert_data',
        python_callable=postgres_connection_task_insert_data
    )

    task4 = PythonOperator(
        task_id='pg_conn_delete_data',
        python_callable=postgres_connection_task_delete_data
    )
    task1 >> task2 >> task3 >> task4