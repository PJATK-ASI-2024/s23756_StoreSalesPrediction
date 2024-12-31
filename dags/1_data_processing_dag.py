from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Funkcja do pobrania danych z Google Sheets
def fetch_data_from_gsheets(sheet_name, **kwargs):
    scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/Michal/airflow/credentials/omega-cosmos-441816-r6-681c8bd64417.json', scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open(sheet_name).sheet1
    data = pd.DataFrame(worksheet.get_all_records())
    kwargs['ti'].xcom_push(key='raw_data', value=data.to_dict())

# Funkcja do czyszczenia danych
def clean_data(**kwargs):
    data = pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='fetch_data', key='raw_data'))
    data = data.drop_duplicates()
    data = data.fillna(data.mean())  # obsługa brakujących wartości
    kwargs['ti'].xcom_push(key='cleaned_data', value=data.to_dict())

# Funkcja do standaryzacji i normalizacji danych
def scale_data(**kwargs):
    data = pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='clean_data', key='cleaned_data'))
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    normalizer = MinMaxScaler()
    data_normalized = normalizer.fit_transform(data_scaled)
    scaled_data = pd.DataFrame(data_normalized, columns=data.columns)
    kwargs['ti'].xcom_push(key='scaled_data', value=scaled_data.to_dict())

# Funkcja do zapisu danych do Google Sheets
def save_to_gsheets(sheet_name, **kwargs):
    data = pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='scale_data', key='scaled_data'))
    # Konfiguracja OAuth
    scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('C:/Users/Michal/airflow/credentials/omega-cosmos-441816-r6-681c8bd64417.json', scope)
    gc = gspread.authorize(credentials)
    
    # Tworzenie lub otwieranie arkusza
    try:
        sh = gc.open(sheet_name)
        worksheet = sh.get_worksheet(0)  # Wybiera pierwszy arkusz
    except gspread.exceptions.SpreadsheetNotFound:
        sh = gc.create(sheet_name)
        worksheet = sh.get_worksheet(0)  # Tworzy pierwszy arkusz
    
    # Zapisanie danych do arkusza
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())

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
        python_callable=fetch_data_from_gsheets,
        op_args=['Zbior_Modelowy']
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
        python_callable=save_to_gsheets,
        op_args=['Processed_Data']
    )

    t1 >> t2 >> t3 >> t4
