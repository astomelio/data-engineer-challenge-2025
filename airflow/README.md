# Airflow Pipeline for Loan Data

This directory contains the Airflow setup to orchestrate the loan data pipeline: Excel → RAW → SILVER → GOLD.

## Project Structure

```
airflow/
├── dags/
│   └── loan_pipeline_dag.py          # Main DAG definition
├── utils/
│   ├── __init__.py                   # Package exports
│   ├── pipeline_functions.py         # Business logic functions
│   └── config.py                     # Configuration settings
├── docker-compose.yml                # Airflow stack setup
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Pipeline Overview

The DAG `loan_data_pipeline` consists of the following tasks:

1. **ingest_excel_to_raw**: Runs the ingestion script to load Excel data into RAW layer (Parquet + DuckDB)
2. **dbt_deps**: Installs dbt dependencies
3. **dbt_run_models**: Executes dbt models to create SILVER and GOLD layers
4. **dbt_run_tests**: Runs data quality tests
5. **validate_data_quality**: Additional data quality validation
6. **dbt_generate_docs**: Generates dbt documentation

## Architecture Benefits

### Utils Organization
- **`pipeline_functions.py`**: Contains all business logic, making the DAG clean and focused
- **`config.py`**: Centralized configuration management
- **Separation of concerns**: DAG definition vs. business logic vs. configuration

### Maintainability
- Easy to add new pipeline functions
- Configuration changes don't require DAG modifications
- Clear structure for team collaboration

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for Docker

### Setup and Run

1. **Set Airflow UID** (macOS/Linux):
   ```bash
   echo -e "AIRFLOW_UID=$(id -u)" > .env
   ```

2. **Start Airflow**:
   ```bash
   docker-compose up -d
   ```

3. **Access Airflow UI**:
   - Open http://localhost:8080
   - Login: admin/admin

4. **Enable and Run DAG**:
   - Find `loan_data_pipeline` in the DAGs list
   - Toggle the DAG to enable it
   - Click "Trigger DAG" to run manually

## Configuration

### Environment Variables

For production deployment, set these environment variables:

```bash
# Production mode (enables S3 upload)
ENVIRONMENT=production
RAW_S3_BUCKET=your-s3-bucket
RAW_S3_PREFIX=raw/loans

# Airflow credentials
_AIRFLOW_WWW_USER_USERNAME=your-username
_AIRFLOW_WWW_USER_PASSWORD=your-password
```

### Customizing Configuration

Edit `utils/config.py` to modify:
- DAG settings (schedule, retries, etc.)
- Task configurations
- Data quality thresholds
- Environment variables

## Development

### Adding New Tasks

1. Add function to `utils/pipeline_functions.py`
2. Add configuration to `utils/config.py`
3. Import and use in `dags/loan_pipeline_dag.py`

### Testing Individual Functions

```bash
# Test pipeline functions locally
python -c "
from utils.pipeline_functions import run_ingestion
run_ingestion()
"
```

### Manual DAG Testing
```bash
# Test individual tasks
airflow tasks test loan_data_pipeline ingest_excel_to_raw 2024-01-01
airflow tasks test loan_data_pipeline dbt_run_models 2024-01-01
```

## Monitoring

- **Airflow UI**: http://localhost:8080
- **DAG Status**: Monitor task success/failure in the UI
- **Logs**: View detailed logs for each task
- **Data Quality**: Check dbt test results and custom validation

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure AIRFLOW_UID is set correctly
2. **Memory Issues**: Increase Docker memory allocation
3. **Port Conflicts**: Change port 8080 if already in use
4. **Import Errors**: Check that utils folder is properly mounted

### Reset Airflow
```bash
docker-compose down -v
docker-compose up -d
```

## Production Considerations

- Use external database (PostgreSQL/MySQL) instead of SQLite
- Configure proper authentication and authorization
- Set up monitoring and alerting
- Use Kubernetes for scaling
- Configure proper logging and metrics
- Add more comprehensive data quality checks in `validate_data_quality`
