# Data Engineer Challenge 2025 – Delivery

---

## Context

The challenge was to act as a **Data Engineer** within a team of Data Scientists and Analysts, and deliver a pipeline that:

- Ingests a new dataset (Excel).
- Profiles and evaluates **data quality**.
- Proposes a **data model and storage structure** for analytics.
- Builds a reproducible pipeline.

I implemented this locally using **DuckDB + dbt + Apache Airflow**, simulating a warehouse in **lakehouse layers (Raw → Silver → Gold)**.

## Step 1 – Data Profiling

Before modeling, I performed a structured profiling in order to understand the data we were working on. 

**Findings:**

- **Duplicates:** 18.0% identical rows (18,001 out of 100,000 records).
- **Nulls:** `Credit Score` (~20.7%), `Annual Income` (~20.7%), `Months since last delinquent` (~53%).
- **Outliers:** sentinel `Current Loan Amount = 99,999,999`; mis-scaled `Credit Score > 900`.
- **Inconsistent categories:** `Home Ownership` and `Purpose` values with mixed cases and underscores.
- **String fields needing normalization:** `Years in current job` with text like "10+ years".

👉 These issues informed the cleaning rules in the Silver layer.

## Step 2 – Data Lakehouse Layers Design

The system simulates the way an **S3 bucket feeds a data warehouse**:

- **Landing (Excel → pseudo-S3):** the raw Excel file is the "landing zone".
- **RAW layer:** Python script copies data from landing into DuckDB → `raw.raw_loans`.
- **SILVER layer:** dbt model `silver_loans` cleans, normalizes, and enforces business rules.
- **GOLD layer:** star schema with `fact_loan`, `dim_customer`, `dim_purpose` for analytics and dashboards.

This ensures **traceability**: you can always go back to the unmodified raw data.

### Production Architecture Vision
- **Development (Current)**: RAW stored in local DuckDB
- **Production (AWS)**: RAW should be stored in S3 buckets with partitioning
- **Migration**: Script includes S3 functionality for production deployment

## Step 3 – Physical Data Model

I built a **lean star schema** at the **loan level**:

- **Fact table – `fact_loan`:** metrics about each loan (amount, score, income, balances, bankruptcies, status, term).
- **Dimensions:**
    - `dim_customer`: customer attributes (job tenure, home ownership).
    - `dim_purpose`: normalized loan purposes.

**Why this design?**

- Focuses the fact on what analysts actually measure.
- Keeps the main segmentation axes in dimensions (who & why).
- Easy to extend later (new facts like `fact_payment`, new dims like `dim_date`).

**Implementation**: We used dbt for testing and model creation with comprehensive data quality tests.

## Step 4 – Pipeline Flow

- **Input:** Excel is dropped in the landing folder (simulating S3).
- **Ingestion:** Python script loads the Excel and persists it to DuckDB (`raw.raw_loans`).
- **Transformation:** dbt creates Silver & Gold layers.
- **Validation:** dbt tests check ranges, not-null, accepted values, and relationships.
- **Documentation:** lineage visible in `dbt docs`.
- **Orchestration:** Apache Airflow manages the entire pipeline with error handling and monitoring.

## Step 5 – Data Quality Implementation

### Silver Layer Cleaning Rules
- **Deduplication**: `ROW_NUMBER() OVER (PARTITION BY loan_id ORDER BY loan_id)` to remove 18% duplicates
- **Sentinel Values**: `NULLIF("Current Loan Amount", 99999999)` for invalid amounts
- **Credit Score Normalization**: `CASE WHEN "Credit Score" > 900 THEN ROUND("Credit Score"/10.0)`
- **Categorical Standardization**: `REPLACE(COALESCE(NULLIF(TRIM("Purpose"), ''), 'Other'), '_', ' ')`
- **Job Tenure Parsing**: `TRY_CAST(REGEXP_EXTRACT(COALESCE("Years in current job", ''), '([0-9]+)', 1) AS INT)`

### Data Quality Tests
- **Not Null Tests**: Critical fields like `loan_id`, `customer_id`
- **Unique Tests**: `loan_id` uniqueness in fact table
- **Accepted Values**: Valid loan statuses and home ownership values
- **Range Tests**: Credit scores between 300-850, positive loan amounts
- **Custom Tests**: Business logic validation

## Step 6 – Orchestration with Apache Airflow

### Pipeline DAGs
- **`loan_data_pipeline`**: Full refresh mode for complete reprocessing
- **`loan_data_pipeline_incremental`**: Incremental mode for new data additions

### Task Structure
1. **Ingestion Task**: Excel → RAW layer (DuckDB)
2. **Silver Transformation**: dbt run for SILVER layer
3. **Gold Transformation**: dbt run for GOLD layer
4. **Data Quality Validation**: dbt test execution
5. **Documentation Generation**: dbt docs generation

### Error Handling & Monitoring
- **Fail-fast**: Pipeline stops on any task failure
- **Retry Logic**: Configurable retry attempts for transient failures
- **Logging**: Comprehensive task logs for debugging
- **Web UI**: Real-time monitoring at http://localhost:8080

## 📊 Results

### Data Statistics
- **RAW**: 100,000 original records (`raw.raw_loans`)
- **SILVER**: 81,999 records (18.0% duplicates removed) (`silver.silver_loans`)
- **GOLD**: 
  - Fact Table: 81,999 records (`gold.fact_loan`)
  - Dim Customer: 81,999 unique customers (`gold.dim_customer`)
  - Dim Purpose: 16 unique purposes (`gold.dim_purpose`)

### Business Insights
- **Loan Status Distribution**: 72.4% Fully Paid, 27.6% Charged Off
- **Primary Purpose**: 79.2% Debt Consolidation
- **Credit Score Average**: 720.2 (Good range)
- **Home Ownership**: 48.8% Mortgage, 42.1% Rent, 9.1% Own

### Example Analytics Query
```sql
SELECT 
    p.purpose_name, 
    f.loan_status, 
    AVG(f.credit_score) as avg_score,
    COUNT(*) as loan_count
FROM gold.fact_loan f
JOIN gold.dim_purpose p USING (purpose_id)
GROUP BY 1,2
ORDER BY loan_count DESC;
```

## 🚨 Production Operations (Vision)

Although this is a local proof of concept, in a production scenario this pipeline would include:

### Infrastructure
- **S3 Storage**: Raw data in partitioned S3 buckets
- **Data Warehouse**: Snowflake/BigQuery for analytical workloads
- **Container Orchestration**: Kubernetes for Airflow deployment
- **Monitoring**: DataDog/New Relic for pipeline observability

### Operational Features
- **Error handling** (fail-fast on ingestion/transformation errors)
- **Alerts/notifications** on data quality or job failures
- **Retries & recovery** for ingestion jobs
- **Monitoring dashboards** for job success/failure and data freshness
- **Data lineage tracking** for compliance and debugging
- **Automated testing** in CI/CD pipeline

### Scalability Considerations
- **Incremental processing** for large datasets
- **Partitioning strategy** for time-based data
- **Resource optimization** for cost efficiency
- **Data versioning** for reproducibility

## 🛠️ Technical Implementation Details

### Technology Stack
- **Database**: DuckDB (embedded analytical database)
- **Transformation**: dbt-core 1.10.9+ with DuckDB adapter
- **Orchestration**: Apache Airflow 3.0.4+
- **Language**: Python 3.13+
- **Data Format**: Parquet for efficient storage

### Project Structure
```
data_engineer_challenge_local_duckdb/
├── data/                          # Source data
├── ingest/                        # Ingestion scripts
├── dbt/                          # dbt transformations
│   ├── models/silver/            # SILVER layer
│   ├── models/gold/              # GOLD layer
│   └── dbt_project.yml
├── airflow/                      # Airflow orchestration
│   ├── dags/                     # Pipeline DAGs
│   └── utils/                    # Shared functions
├── scripts/                      # Utility scripts
└── docs/                         # Documentation
```

### Key Features
- ✅ **Scalability**: Ready for S3 in production (RAW layer)
- ✅ **Data Quality**: Automatic tests and validation
- ✅ **Documentation**: Auto-generated documentation
- ✅ **Monitoring**: Airflow for orchestration
- ✅ **Flexibility**: Multiple execution options
- ✅ **Incremental Processing**: Support for both full refresh and incremental modes

## ✅ Key Takeaways

- Simulates **landing → raw → silver → gold** just like an S3-backed warehouse
- **Data quality issues** were identified and corrected before modeling (18% duplicates removed)
- **Fact/dim design** is clear, business-oriented, and scalable
- **Pipeline vision** includes error management and alerting for long-run reliability
- **Production-ready architecture** with clear migration path to cloud infrastructure
- **Comprehensive testing** ensures data quality and pipeline reliability

---

*This implementation demonstrates enterprise-grade data engineering practices in a local development environment, ready for production deployment.*
