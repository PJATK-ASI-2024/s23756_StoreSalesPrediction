from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Definicja domyślnych argumentów DAG-a
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Tworzenie DAG-a
dag = DAG(
    '6_contenerysation_and_api',
    default_args=default_args,
    description='DAG do tworzenia API, budowania kontenera Dockera i publikowania obrazu',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
)

# Task 1: Tworzenie API
create_api = BashOperator(
    task_id='create_api',
    bash_command='''
    echo "Tworzenie API FastAPI" && \
    mkdir -p /tmp/fastapi_app && \
    echo "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {\"Hello\": \"World\"}" > /tmp/fastapi_app/main.py && \
    echo "fastapi" > /tmp/fastapi_app/requirements.txt
    ''',
    dag=dag,
)

# Task 2: Budowanie obrazu Dockera
build_docker_image = BashOperator(
    task_id='build_docker_image',
    bash_command='''
    echo "Budowanie obrazu Dockera" && \
    cd /tmp/fastapi_app && \
    echo "FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]" > Dockerfile && \
    docker build -t my_fastapi_app .
    ''',
    dag=dag,
)

# Task 3: Publikacja obrazu na Docker Hub
publish_docker_image = BashOperator(
    task_id='publish_docker_image',
    bash_command='''
    echo "Publikowanie obrazu Dockera" && \
    docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD && \
    docker tag my_fastapi_app $DOCKER_USERNAME/my_fastapi_app:latest && \
    docker push $DOCKER_USERNAME/my_fastapi_app:latest
    ''',
    env={
        'DOCKER_USERNAME': 'twoja_nazwa_uzytkownika',
        'DOCKER_PASSWORD': 'twoje_haslo',
    },
    dag=dag,
)

# Ustalanie kolejności zadań
create_api >> build_docker_image >> publish_docker_image
