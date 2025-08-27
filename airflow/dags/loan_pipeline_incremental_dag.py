from datetime import datetime, timedelta
import os
import subprocess
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

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

# Update default_args for incremental DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Incremental DAG definition
incremental_dag = DAG(
    'loan_data_pipeline_incremental',
    default_args=default_args,
    description='Loan data pipeline with incremental ingestion mode',
    schedule='@daily',  # Run daily for incremental updates
    catchup=False,
    tags=['incremental', 'loans', 'data-pipeline'],
)

# Task definitions for incremental mode
incremental_ingest_task = PythonOperator(
    task_id='ingest_excel_incremental',
    python_callable=run_ingestion,
    params={'mode': 'incremental'},  # Pass mode as parameter
    dag=incremental_dag,
)

dbt_deps_task = PythonOperator(
    task_id='dbt_deps',
    python_callable=run_dbt_deps,
    dag=incremental_dag,
)

dbt_run_task = PythonOperator(
    task_id='dbt_run_models',
    python_callable=run_dbt_models,
    dag=incremental_dag,
)

dbt_test_task = PythonOperator(
    task_id='dbt_run_tests',
    python_callable=run_dbt_tests,
    dag=incremental_dag,
)

data_quality_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=incremental_dag,
)

dbt_docs_task = PythonOperator(
    task_id='dbt_generate_docs',
    python_callable=generate_dbt_docs,
    dag=incremental_dag,
)

# Task dependencies for incremental pipeline
incremental_ingest_task >> dbt_deps_task >> dbt_run_task >> dbt_test_task >> data_quality_task >> dbt_docs_task
