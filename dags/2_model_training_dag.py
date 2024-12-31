from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Funkcja do pobrania danych
def download_data(**kwargs):
    try:
        # plik znajduje się lokalnie
        data = pd.read_csv('C:/Users/Michal/Desktop/train.csv')
        kwargs['ti'].xcom_push(key='data', value=data.to_dict())
    except Exception as e:
        raise ValueError(f"Problem z pobieraniem danych: {e}")

# Funkcja do podziału danych
def split_data(**kwargs):
    data = pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='download_data', key='data'))
    train, test = train_test_split(data, test_size=0.3, random_state=42)
    kwargs['ti'].xcom_push(key='train_data', value=train.to_dict())
    kwargs['ti'].xcom_push(key='test_data', value=test.to_dict())

# Funkcja do zapisu danych do Google Sheets
def save_to_gsheets(sheet_name, data):
    try:
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
        df = pd.DataFrame(data)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        raise ValueError(f"Problem z zapisem do Google Sheets: {e}")

# DAG definicja
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

with DAG('dag_data_split',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id='download_data',
        python_callable=download_data
    )

    t2 = PythonOperator(
        task_id='split_data',
        python_callable=split_data
    )

    t3 = PythonOperator(
        task_id='save_train_to_gsheets',
        python_callable=lambda **kwargs: save_to_gsheets(
            'Zbior_Modelowy', 
            pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='split_data', key='train_data'))
        )
    )

    t4 = PythonOperator(
        task_id='save_test_to_gsheets',
        python_callable=lambda **kwargs: save_to_gsheets(
            'Zbior_Douczeniowy', 
            pd.DataFrame(kwargs['ti'].xcom_pull(task_ids='split_data', key='test_data'))
        )
    )

    # Ustalamy zależności między zadaniami
    t1 >> t2 >> [t3, t4]
