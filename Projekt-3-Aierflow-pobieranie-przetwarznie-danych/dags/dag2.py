from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Funkcja do pobrania danych z Google Sheets
def fetch_data_from_gsheets(sheet_name):
    scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/Michal/airflow/credentials/omega-cosmos-441816-r6-681c8bd64417.json', scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open(sheet_name).sheet1
    data = pd.DataFrame(worksheet.get_all_records())
    return data

# Funkcja do czyszczenia danych
def clean_data(data):
    data = data.drop_duplicates()
    data = data.fillna(data.mean())  # obsługa brakujących wartości
    return data

# Funkcja do standaryzacji i normalizacji danych
def scale_data(data):
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    normalizer = MinMaxScaler()
    data_normalized = normalizer.fit_transform(data_scaled)
    return pd.DataFrame(data_normalized, columns=data.columns)

# DAG definicja
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

with DAG('dag_data_processing',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id='fetch_data',
        python_callable=lambda: fetch_data_from_gsheets('Zbior_Modelowy')
    )

    t2 = PythonOperator(
        task_id='clean_data',
        python_callable=lambda **kwargs: clean_data(
            kwargs['ti'].xcom_pull(task_ids='fetch_data')
        )
    )

    t3 = PythonOperator(
        task_id='scale_data',
        python_callable=lambda **kwargs: scale_data(
            kwargs['ti'].xcom_pull(task_ids='clean_data')
        )
    )

    t4 = PythonOperator(
        task_id='save_processed_data',
        python_callable=lambda **kwargs: save_to_gsheets(
            'Processed_Data', 
            kwargs['ti'].xcom_pull(task_ids='scale_data')
        )
    )

    t1 >> t2 >> t3 >> t4
