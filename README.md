# 🚀 Data Engineer Challenge - Loan Pipeline

## 📋 Overview

This project implements a **complete data pipeline** to process loan information from an Excel file to an optimized dimensional model for analytics. The pipeline follows the **RAW → SILVER → GOLD** architecture and uses **Apache Airflow** for orchestration.

## 🏗️ Pipeline Architecture

### 📊 Data Layers

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LANDING       │    │     SILVER      │    │      GOLD       │
│   (RAW)         │───▶│   (Structured)  │───▶│   (Analytics)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│ • Excel Source  │    │ • Cleaned Data  │    │ • Fact Tables   │
│ • Parquet Files │    │ • Deduplication │    │ • Dimensions    │
│ • Raw Tables    │    │ • Validation    │    │ • Star Schema   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 Data Flow

1. **LANDING (RAW)**: Original Excel data → `raw.raw_loans` in DuckDB
2. **SILVER**: Cleaned and structured data → `silver.silver_loans`
3. **GOLD**: Dimensional model for analytics → `gold.fact_loan`, `gold.dim_*`

### ⚠️ **Current vs Production Architecture**
- **Development (Current)**: RAW stored in local DuckDB
- **Production (AWS)**: RAW should be stored in S3 buckets
- **Migration**: Script includes S3 functionality for production

## 📁 Project Structure

```
data_engineer_challenge_local_duckdb/
├── 📊 data/                          # Source data
│   └── Data Engineer Challenge.xlsx  # Original Excel file
├── 🔧 ingest/                        # Ingestion scripts
│   └── ingest_excel_to_duckdb.py    # Initial processing
├── 🎯 dbt/                          # dbt transformations
│   ├── models/
│   │   ├── silver/                  # SILVER layer
│   │   │   └── silver_loans.sql     # Cleaning and deduplication
│   │   └── gold/                    # GOLD layer
│   │       ├── dim_customer.sql     # Customer dimension
│   │       ├── dim_purpose.sql      # Purpose dimension
│   │       └── fact_loan.sql        # Fact table
│   ├── dbt_project.yml
│   └── packages.yml
├── ☁️ airflow/                      # Airflow orchestration
│   ├── dags/
│   │   ├── loan_pipeline_dag.py
│   │   └── loan_pipeline_incremental_dag.py
│   └── utils/
│       ├── pipeline_functions.py
│       └── config.py
├── 📜 scripts/                      # Utility scripts
│   ├── run_pipeline.py
│   ├── explore_db.py
│   └── quick_stats.py
├── 📚 docs/                         # Technical documentation
│   ├── COMPLETE_DOCUMENTATION.md
│   ├── NULL_MEANING_ANALYSIS.md
│   └── dbt_documentation.md
└── 📚 README.md                     # This documentation
```

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.13+
- Apache Airflow 3.0.4+
- dbt-core 1.10.9+
- DuckDB

### 🔧 Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd data_engineer_challenge_local_duckdb
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Airflow**
```bash
export AIRFLOW_HOME=$(pwd)/airflow
export PYTHONPATH=$PYTHONPATH:$(pwd)/airflow
airflow standalone
```

### 🎯 Execution

#### Option 1: Local Pipeline
```bash
python scripts/run_pipeline.py
```

#### Option 2: Pipeline with Airflow
1. Access http://localhost:8080 (admin/cvPPAEfuV7bSTP6s)
2. Find DAG `loan_data_pipeline`
3. Click "Trigger DAG"

#### Option 3: Explore Database
```bash
python scripts/explore_db.py
```

#### Option 4: Quick Statistics
```bash
python scripts/quick_stats.py
```

## 📊 Pipeline Results

### 📈 Data Statistics
- **RAW**: 100,000 original records (`raw.raw_loans`)
- **SILVER**: 81,999 records (18% duplicates removed) (`silver.silver_loans`)
- **GOLD**: 
  - Fact Table: 81,999 records (`gold.fact_loan`)
  - Dim Customer: 81,999 unique customers (`gold.dim_customer`)
  - Dim Purpose: 16 unique purposes (`gold.dim_purpose`)

### 🎯 Status Distribution
- **Fully Paid**: 59,360 (72.4%)
- **Charged Off**: 22,639 (27.6%)

### 📋 Main Purposes
- **Debt Consolidation**: 64,907 (79.2%)
- **Home Improvements**: 4,795 (5.8%)
- **Other**: 7,238 (8.8%)

## 📚 Technical Documentation

For detailed information about each component:

- **[Complete Documentation](docs/COMPLETE_DOCUMENTATION.md)** - Full technical overview
- **[NULL Analysis](docs/NULL_MEANING_ANALYSIS.md)** - Business meaning of NULL values
- **[dbt Documentation](docs/dbt_documentation.md)** - Transformations and models

## 🔧 Useful Commands

### 📊 Monitoring
```bash
# View Airflow logs
tail -f airflow/logs/dag_id/task_id/run_id/task_id.log

# Run dbt with debug
cd dbt && dbt run --log-level debug

# List your project DAGs
bash airflow/scripts/my_dags.sh
```

### 🧹 Maintenance
```bash
# Clean dbt
cd dbt && dbt clean

# Reprocess from scratch
python scripts/run_pipeline.py

# Generate dbt docs
cd dbt && dbt docs generate && dbt docs serve
```

## 🎯 Key Features

- ✅ **Scalability**: Ready for S3 in production (RAW layer)
- ✅ **Data Quality**: Automatic tests and validation
- ✅ **Documentation**: Auto-generated documentation
- ✅ **Monitoring**: Airflow for orchestration
- ✅ **Flexibility**: Multiple execution options
- ✅ **Incremental Processing**: Support for both full refresh and incremental modes

## 🚀 Next Steps

- Implement data quality alerts
- Add more business tests
- Optimize for larger volumes
- Implement data versioning
- Add data lineage visualization

---

*Loan Pipeline v1.0 - Professional documentation for enterprise presentation*