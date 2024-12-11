from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime

# Definicja DAG
with DAG('example_dag', start_date=datetime(2024, 1, 1), schedule_interval='@daily') as dag:
    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    start >> end
