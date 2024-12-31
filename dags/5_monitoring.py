from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
import pickle
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score

MODEL_PATH = "/mnt/data/model.pkl"
DATA_PATH = "/mnt/data/data.csv"
CRITICAL_THRESHOLD = 0.8

def load_model():
    """Załadowanie modelu."""
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def evaluate_model(ti):
    """Ocena jakości modelu na nowych danych."""
    model = load_model()
    data = pd.read_csv(DATA_PATH)
    X, y = data.iloc[:, :-1], data.iloc[:, -1]
    predictions = model.predict(X)
    
    accuracy = accuracy_score(y, predictions)
    precision = precision_score(y, predictions, average="weighted")
    recall = recall_score(y, predictions, average="weighted")
    
    ti.xcom_push(key='metrics', value={'accuracy': accuracy, 'precision': precision, 'recall': recall})
    
    if accuracy < CRITICAL_THRESHOLD:
        ti.xcom_push(key='alert', value=True)
        ti.xcom_push(key='reason', value=f"Accuracy poniżej progu: {accuracy:.2f} < {CRITICAL_THRESHOLD:.2f}")
    else:
        ti.xcom_push(key='alert', value=False)

def run_tests(ti):
    """Uruchomienie testów jednostkowych na modelu i pipeline'ie."""
    alert = False
    failed_tests = []

    try:
        model = load_model()
        assert model is not None, "Model nie został poprawnie załadowany"
    except AssertionError as e:
        alert = True
        failed_tests.append(str(e))

    try:
        empty_data = pd.DataFrame()
        model.predict(empty_data)
    except Exception as e:
        failed_tests.append(f"Błąd obsługi pustych danych: {e}")
        alert = True

    if alert:
        ti.xcom_push(key='alert', value=True)
        ti.xcom_push(key='reason', value=f"Nieudane testy: {', '.join(failed_tests)}")
    else:
        ti.xcom_push(key='alert', value=False)

def send_alert(ti):
    """Wysłanie maila z raportem, jeśli którykolwiek test zawiódł."""
    alert = ti.xcom_pull(task_ids='evaluate_model', key='alert') or ti.xcom_pull(task_ids='run_tests', key='alert')
    reason = ti.xcom_pull(task_ids='evaluate_model', key='reason') or ti.xcom_pull(task_ids='run_tests', key='reason')
    metrics = ti.xcom_pull(task_ids='evaluate_model', key='metrics')

    if alert:
        subject = "Model Monitoring Alert"
        body = f"""
        Model Monitoring Alert:
        
        - Powód: {reason}
        - Metryki:
          - Accuracy: {metrics['accuracy']:.2f}
          - Precision: {metrics['precision']:.2f}
          - Recall: {metrics['recall']:.2f}
        """
        ti.xcom_push(key='email_subject', value=subject)
        ti.xcom_push(key='email_body', value=body)

# Konfiguracja DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email': ['michas12wp.pl@wp.pl']
}

with DAG('model_validation_monitoring',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    evaluate_task = PythonOperator(
        task_id='evaluate_model',
        python_callable=evaluate_model
    )

    test_task = PythonOperator(
        task_id='run_tests',
        python_callable=run_tests
    )

    send_alert_task = PythonOperator(
        task_id='send_alert',
        python_callable=send_alert
    )

    send_email_task = EmailOperator(
        task_id='send_email',
        to='michas12wp.pl@wp.pl',  
        subject="{{ task_instance.xcom_pull(task_ids='send_alert', key='email_subject') }}",
        html_content="{{ task_instance.xcom_pull(task_ids='send_alert', key='email_body') }}",
    )

    # Kolejność w DAG
    evaluate_task >> test_task >> send_alert_task >> send_email_task
