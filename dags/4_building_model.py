from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import joblib

def process_data():
    # Ścieżki do plików
    raw_data_path = '/opt/airflow/data/train.csv'
    processed_data_path = '/opt/airflow/processed_data/processed_data.csv'

    # Wczytaj dane źródłowe
    data = pd.read_csv(raw_data_path)

    # Usuń zbędne kolumny
    columns_to_drop = ['Row ID', 'Order ID', 'Customer ID', 'Customer Name', 'Product ID', 'Product Name']
    data = data.drop(columns=columns_to_drop)

    # Uzupełnij brakujące wartości
    data['Postal Code'].fillna(-1, inplace=True)

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

def train_model():
    # Ścieżki do plików
    processed_data_path = '/opt/airflow/processed_data/processed_data.csv'
    model_path = '/opt/airflow/models/model.pkl'
    report_path = '/opt/airflow/reports/evaluation_report.txt'

    # Wczytaj przetworzone dane
    processed_data = pd.read_csv(processed_data_path)

    # Podziel dane na cechy i zmienną docelową
    X = processed_data.drop(columns=['Sales'])
    y = processed_data['Sales']

    # Podziel dane na zbiory treningowy i testowy
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Trenuj model (Random Forest jako przykładowy model)
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    # Ewaluacja modelu (MSE i R² dla regresji)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Zapisz model
    joblib.dump(model, model_path)

    # Zapisz raport z ewaluacji
    with open(report_path, 'w') as report_file:
        report_file.write(f'Mean Squared Error: {mse}\n')
        report_file.write(f'R-squared: {r2}\n')
        report_file.write('\nPrzewidywania vs Rzeczywiste wartości:\n')
        report_file.write(f'Pierwsze 5 przewidywanych: {y_pred[:5]}\n')
        report_file.write(f'Pierwsze 5 rzeczywistych: {y_test[:5].values}\n')

# Definicja DAG-a
with DAG(
    dag_id='4_building_model',
    start_date=datetime(2024, 10, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data
    )

    train_model_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model
    )

    process_data_task >> train_model_task
