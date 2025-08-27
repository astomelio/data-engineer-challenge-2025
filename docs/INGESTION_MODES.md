# 📊 Ingestion Modes - Full Refresh vs Incremental

## 📋 Overview

The ingestion script now supports two modes for processing Excel data:

- **Full Refresh**: Replace all existing data (initial load or complete replacement)
- **Incremental**: Append new data to existing tables (daily updates)

## 🔄 Full Refresh Mode

### Purpose
- Initial data load
- Complete data replacement
- Data quality issues requiring full reload

### Usage
```bash
python ingest/ingest_excel_to_duckdb.py \
    --excel "data/Data Engineer Challenge.xlsx" \
    --duckdb "dbt/data_challenge.duckdb" \
    --raw_dir "raw_data" \
    --mode "full_refresh"
```

### What it does:
1. **Drops** existing `raw.raw_loans` table
2. **Creates** new table from Excel file
3. **Replaces** all data completely
4. **Generates** timestamped Parquet files

### Output:
- `raw_data/raw_loans_full_refresh_YYYYMMDD_HHMMSS_<hash>.parquet`
- Fresh `raw.raw_loans` table in DuckDB

## ➕ Incremental Mode

### Purpose
- Daily updates with new Excel files
- Adding new data without losing existing data
- Processing multiple Excel files from a directory

### Usage Examples

#### **Process all Excel files in a directory:**
```bash
python ingest/ingest_excel_to_duckdb.py \
    --excel_dir "data" \
    --duckdb "dbt/data_challenge.duckdb" \
    --raw_dir "raw_data" \
    --mode "incremental"
```

#### **Process only specific files (using pattern):**
```bash
# Only files starting with "new_"
python ingest/ingest_excel_to_duckdb.py \
    --excel_dir "data" \
    --excel_pattern "new_*.xlsx" \
    --duckdb "dbt/data_challenge.duckdb" \
    --mode "incremental"

# Only files from today
python ingest/ingest_excel_to_duckdb.py \
    --excel_dir "data" \
    --excel_pattern "*2025-01-15*.xlsx" \
    --duckdb "dbt/data_challenge.duckdb" \
    --mode "incremental"
```

### What it does:
1. **Scans** directory for Excel files (with optional pattern)
2. **Processes** each file individually
3. **Appends** data to existing `raw.raw_loans` table
4. **Adds** metadata columns:
   - `_source_file`: Name of the Excel file
   - `_ingestion_timestamp`: When the data was processed

### Output:
- `raw_data/raw_loans_incremental_YYYYMMDD_HHMMSS_<hash>.parquet`
- Updated `raw.raw_loans` table with appended data

## 🎯 Airflow Integration

### Full Refresh DAG
```python
# airflow/dags/loan_pipeline_dag.py
ingest_task = PythonOperator(
    task_id='ingest_excel_to_raw',
    python_callable=run_ingestion,
    params={'mode': 'full_refresh'},
    dag=dag,
)
```

### Incremental DAG
```python
# airflow/dags/loan_pipeline_incremental_dag.py
incremental_ingest_task = PythonOperator(
    task_id='ingest_excel_incremental',
    python_callable=run_ingestion,
    params={'mode': 'incremental'},
    dag=incremental_dag,
)
```

## 📁 Directory Structure for Incremental Mode

```
data/
├── Data Engineer Challenge.xlsx          # Main file (full refresh)
├── new_loans_2025_01_15.xlsx            # New file 1
├── new_loans_2025_01_16.xlsx            # New file 2
├── additional_data.xlsx                  # New file 3
├── daily_update_*.xlsx                   # Pattern-based files
└── ...
```

### **💡 Practical Approach:**
- **No special folders needed** - just put new Excel files in the same `data/` directory
- **Use patterns** to process only specific files when needed
- **Flexible** - can process all files or just selected ones

## 🔧 Environment Variables

### Development
```bash
export ENVIRONMENT=development
export INGESTION_MODE=full_refresh  # or incremental
```

### Production
```bash
export ENVIRONMENT=production
export INGESTION_MODE=incremental
export RAW_S3_BUCKET=my-raw-data-bucket
export RAW_S3_PREFIX=raw/loans
```

## 📊 Metadata Columns (Incremental Mode)

When using incremental mode, the following columns are automatically added:

| Column | Type | Description |
|--------|------|-------------|
| `_source_file` | VARCHAR | Name of the Excel file that contained this record |
| `_ingestion_timestamp` | TIMESTAMP | When the record was processed |

### Example Query
```sql
SELECT 
    loan_id,
    customer_id,
    _source_file,
    _ingestion_timestamp
FROM raw.raw_loans
WHERE _source_file = 'new_loans_2025_01_15.xlsx'
ORDER BY _ingestion_timestamp DESC;
```

## 🚀 Demo Script

Run the demo to see both modes in action:

```bash
python scripts/run_ingestion_modes.py
```

This script will:
1. Run full refresh mode
2. Run incremental mode
3. Show the differences
4. Provide usage tips

## ⚠️ Important Notes

### Full Refresh Mode
- **⚠️ WARNING**: This will delete all existing data
- Use for initial load or complete data replacement
- Single Excel file processing only

### Incremental Mode
- **✅ SAFE**: Appends data without deleting existing records
- Processes all Excel files in the specified directory
- Adds metadata for traceability
- Can be run multiple times safely

### Data Quality
- Both modes include data validation
- Parquet files are created for audit trail
- S3 upload available in production mode

## 🔍 Monitoring

### Check Data Counts
```sql
-- Check total records
SELECT COUNT(*) as total_records FROM raw.raw_loans;

-- Check by source file (incremental mode)
SELECT 
    _source_file,
    COUNT(*) as record_count,
    MIN(_ingestion_timestamp) as first_ingested,
    MAX(_ingestion_timestamp) as last_ingested
FROM raw.raw_loans
GROUP BY _source_file
ORDER BY last_ingested DESC;
```

### Check Parquet Files
```bash
# List all Parquet files
ls -la raw_data/

# Check file sizes
du -h raw_data/*.parquet
```

## 🎯 Best Practices

### When to Use Full Refresh
- Initial data load
- Data quality issues requiring complete reload
- Schema changes
- Monthly/quarterly complete refresh

### When to Use Incremental
- Daily updates
- Adding new data sources
- Regular data feeds
- Production environments

### File Naming Convention
- Use descriptive names: `loans_2025_01_15.xlsx`
- Include dates for easy identification
- Avoid special characters in filenames

---

*Ingestion Modes Documentation v1.0*
