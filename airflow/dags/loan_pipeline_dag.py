from datetime import datetime, timedelta
import os
import subprocess
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import pipeline functions and config from utils
from utils.pipeline_functions import (
    run_ingestion,
    run_dbt_deps,
    run_dbt_models,
    run_dbt_tests,
    generate_dbt_docs,
    validate_data_quality
)
from utils.config import DAG_CONFIG, DEFAULT_ARGS, TASK_CONFIG

# Update default_args to use datetime.now() instead of days_ago
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    DAG_CONFIG['dag_id'],
    default_args=default_args,
    description=DAG_CONFIG['description'],
    schedule=DAG_CONFIG['schedule'],
    catchup=DAG_CONFIG['catchup'],
    tags=DAG_CONFIG['tags'],
)

# Task definitions
ingest_task = PythonOperator(
    task_id=TASK_CONFIG['ingest']['task_id'],
    python_callable=run_ingestion,
    params={'mode': 'full_refresh'},  # Explicitly set full refresh mode
    dag=dag,
)

dbt_deps_task = PythonOperator(
    task_id=TASK_CONFIG['dbt_deps']['task_id'],
    python_callable=run_dbt_deps,
    dag=dag,
)

dbt_run_task = PythonOperator(
    task_id=TASK_CONFIG['dbt_run']['task_id'],
    python_callable=run_dbt_models,
    dag=dag,
)

dbt_test_task = PythonOperator(
    task_id=TASK_CONFIG['dbt_test']['task_id'],
    python_callable=run_dbt_tests,
    dag=dag,
)

data_quality_task = PythonOperator(
    task_id=TASK_CONFIG['data_quality']['task_id'],
    python_callable=validate_data_quality,
    dag=dag,
)

dbt_docs_task = PythonOperator(
    task_id=TASK_CONFIG['dbt_docs']['task_id'],
    python_callable=generate_dbt_docs,
    dag=dag,
)

# Task dependencies
ingest_task >> dbt_deps_task >> dbt_run_task >> dbt_test_task >> data_quality_task >> dbt_docs_task
