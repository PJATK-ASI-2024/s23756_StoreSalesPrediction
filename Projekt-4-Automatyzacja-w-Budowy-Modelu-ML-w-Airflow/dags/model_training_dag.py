from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import joblib

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
    dag_id='model_training_dag',
    start_date=datetime(2024, 10, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    
    train_model_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model
    )
