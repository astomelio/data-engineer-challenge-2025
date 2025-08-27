"""
Configuration settings for the Airflow pipeline.
"""

from datetime import timedelta

# DAG Configuration
DAG_CONFIG = {
    'dag_id': 'loan_data_pipeline',
    'description': 'Loan data pipeline: Excel → RAW → SILVER → GOLD',
    'schedule': timedelta(days=1),
    'catchup': False,
    'tags': ['loan', 'dbt', 'data-pipeline'],
}

# Default Arguments
DEFAULT_ARGS = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Environment Variables
ENV_VARS = {
    'ENVIRONMENT': 'development',  # or 'production'
    'RAW_S3_BUCKET': None,
    'RAW_S3_PREFIX': 'raw/loans',
}

# Task Configuration
TASK_CONFIG = {
    'ingest': {
        'task_id': 'ingest_excel_to_raw',
        'description': 'Ingest Excel data to RAW layer (Parquet + DuckDB)',
    },
    'dbt_deps': {
        'task_id': 'dbt_deps',
        'description': 'Install dbt dependencies',
    },
    'dbt_run': {
        'task_id': 'dbt_run_models',
        'description': 'Run dbt models (SILVER and GOLD layers)',
    },
    'dbt_test': {
        'task_id': 'dbt_run_tests',
        'description': 'Run dbt tests for data quality validation',
    },
    'data_quality': {
        'task_id': 'validate_data_quality',
        'description': 'Additional data quality checks',
    },
    'dbt_docs': {
        'task_id': 'dbt_generate_docs',
        'description': 'Generate dbt documentation',
    },
}

# Data Quality Thresholds
DATA_QUALITY_THRESHOLDS = {
    'min_raw_rows': 1,
    'min_silver_rows': 1,
    'min_gold_rows': 1,
    'max_duplicate_loan_ids': 0,
}
