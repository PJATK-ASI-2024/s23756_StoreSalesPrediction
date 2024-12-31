from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
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
def clean_data(**kwargs):
    data = pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='fetch_data'))
    data = data.drop_duplicates()
    data = data.fillna(data.mean())  # obsługa braków danych
    kwargs['ti'].xcom_push(key='cleaned_data', value=data.to_dict())

# Funkcja do standaryzacji i normalizacji danych
def scale_data(**kwargs):
    data = pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='clean_data', key='cleaned_data'))
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    normalizer = MinMaxScaler()
    data_normalized = normalizer.fit_transform(data_scaled)
    data_processed = pd.DataFrame(data_normalized, columns=data.columns)
    kwargs['ti'].xcom_push(key='processed_data', value=data_processed.to_dict())

# Funkcja do zapisu danych do Google Sheets
def save_to_gsheets(sheet_name, **kwargs):
    scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/Michal/airflow/credentials/omega-cosmos-441816-r6-681c8bd64417.json', scope)
    gc = gspread.authorize(credentials)
    sh = gc.create(sheet_name)
    worksheet = sh.get_worksheet(0)
    data = pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='scale_data', key='processed_data'))
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())

# DAG definicja
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

with DAG('3_download-cloud_clean_standard-normalisate_save',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id='fetch_data',
        python_callable=lambda **kwargs: kwargs['ti'].xcom_push(key='raw_data', value=fetch_data_from_gsheets('Zbior_Modelowy').to_dict())
    )

    t2 = PythonOperator(
        task_id='clean_data',
        python_callable=clean_data
    )

    t3 = PythonOperator(
        task_id='scale_data',
        python_callable=scale_data
    )

    t4 = PythonOperator(
        task_id='save_processed_data',
        python_callable=lambda **kwargs: save_to_gsheets(
            'Processed_Data',
            **kwargs
        )
    )

    t1 >> t2 >> t3 >> t4
