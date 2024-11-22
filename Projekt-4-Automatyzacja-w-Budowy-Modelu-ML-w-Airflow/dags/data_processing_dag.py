from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd

def process_data():
    # Ścieżki do plików
    raw_data_path = '/opt/airflow/data/train.csv'  # Zmień na właściwą ścieżkę do danych źródłowych
    processed_data_path = '/opt/airflow/processed_data/processed_data.csv'
    
    # Wczytaj dane źródłowe
    data = pd.read_csv(raw_data_path)
    
    # Usuń zbędne kolumny
    columns_to_drop = ['Row ID', 'Order ID', 'Customer ID', 'Customer Name', 'Product ID', 'Product Name']
    data = data.drop(columns=columns_to_drop)
    
    # Uzupełnij brakujące wartości
    data['Postal Code'].fillna(-1, inplace=True)  # Wartość -1 oznacza brak
    
    # Przekształć daty i dodaj nowe cechy
    data['Order Date'] = pd.to_datetime(data['Order Date'], format='%d/%m/%Y')
    data['Ship Date'] = pd.to_datetime(data['Ship Date'], format='%d/%m/%Y')
    data['Order Month'] = data['Order Date'].dt.month
    data['Order DayOfWeek'] = data['Order Date'].dt.dayofweek
    data['Shipping Duration'] = (data['Ship Date'] - data['Order Date']).dt.days
    data = data.drop(columns=['Order Date', 'Ship Date'])
    
    # Standaryzuj kolumny numeryczne
    numeric_cols = ['Postal Code', 'Sales', 'Shipping Duration']
    data[numeric_cols] = (data[numeric_cols] - data[numeric_cols].mean()) / data[numeric_cols].std()
    
    # Zakoduj zmienne kategoryczne jako one-hot
    data = pd.get_dummies(data, drop_first=True)
    
    # Zapisz przetworzone dane
    data.to_csv(processed_data_path, index=False)

with DAG(
    dag_id='data_processing_dag',
    start_date=datetime(2024, 10, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    
    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data
    )
