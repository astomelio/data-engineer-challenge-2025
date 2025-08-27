# 📊 dbt Docs Lineage - Visual Example

## 🎯 Data Lineage Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LINEAGE                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAW LAYER     │    │  SILVER LAYER   │    │   GOLD LAYER    │
│                 │    │                 │    │                 │
│  raw.raw_loans  │───▶│ silver_loans    │───▶│   fact_loan     │
│                 │    │                 │    │                 │
│ • 100,000 rows  │    │ • 81,999 rows   │    │ • 81,999 rows   │
│ • Original data │    │ • Cleaned data  │    │ • Analytics     │
│ • No validation │    │ • Deduplicated  │    │ • Star schema   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   DIMENSIONS    │    │   DIMENSIONS    │
                       │                 │    │                 │
                       │ dim_customer    │    │ dim_purpose     │
                       │                 │    │                 │
                       │ • 81,999 rows   │    │ • 7 rows        │
                       │ • Customer attrs│    │ • Purpose types │
                       └─────────────────┘    └─────────────────┘
```

## 🔍 Model Dependencies

### **Source Models**
```
raw.raw_loans
├── Columns: 19
├── Rows: 100,000
├── Tests: 2 (Loan ID, Customer ID not null)
└── Description: Original loan data from Excel file
```

### **Silver Models**
```
silver_loans
├── Source: raw.raw_loans
├── Columns: 19 (cleaned and standardized)
├── Rows: 81,999 (after deduplication)
├── Tests: 4 (not_null, accepted_values, range)
└── Description: Cleaned and standardized loan data
```

### **Gold Models**
```
fact_loan
├── Source: silver_loans + dim_purpose
├── Columns: 19 (fact table)
├── Rows: 81,999
├── Tests: 1 (unique combination)
└── Description: Fact table for loan analytics

dim_customer
├── Source: silver_loans
├── Columns: 3 (customer attributes)
├── Rows: 81,999
└── Description: Customer dimension table

dim_purpose
├── Source: silver_loans
├── Columns: 2 (purpose + surrogate key)
├── Rows: 7
└── Description: Loan purpose dimension table
```

## 📊 Test Results Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        TEST RESULTS                            │
└─────────────────────────────────────────────────────────────────┘

✅ PASSED (5/5 tests)
├── not_null_silver_loans_loan_id
├── not_null_silver_loans_customer_id
├── accepted_values_silver_loans_loan_status
├── dbt_utils_accepted_range_silver_loans_credit_score
└── dbt_utils_unique_combination_of_columns_fact_loan_loan_id

❌ SKIPPED (2/2 source tests - column name issues)
├── source_not_null_raw_raw_loans_Loan_ID
└── source_not_null_raw_raw_loans_Customer_ID
```

## 🎨 dbt Docs Screenshot Example

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 dbt Docs - Data Lineage View                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Sources   │    │   Models    │    │   Tests     │        │
│  │             │    │             │    │             │        │
│  │ raw_loans   │───▶│ silver_loans│───▶│ fact_loan   │        │
│  │             │    │             │    │             │        │
│  │ 100K rows   │    │ 82K rows    │    │ 82K rows    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                │                              │
│                                ▼                              │
│                       ┌─────────────┐                        │
│                       │ dim_customer│                        │
│                       │             │                        │
│                       │ 82K rows    │                        │
│                       └─────────────┘                        │
│                                                                 │
│  📈 Lineage Graph:                                             │
│  • Raw → Silver: Data cleaning & deduplication                │
│  • Silver → Gold: Dimensional modeling                         │
│  • Tests: Data quality validation                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 dbt Commands Used

```bash
# Generate documentation
dbt docs generate

# Serve documentation locally
dbt docs serve

# Run models
dbt run

# Run tests
dbt test

# Show lineage
dbt ls --output name,resource_type,depends_on
```

## 📋 Model Configuration

```yaml
# dbt_project.yml
models:
  data_challenge:
    +materialized: view
    # Silver layer: cleaned and standardized data
    silver:
      +materialized: table
      +schema: silver
    # Gold layer: dimensional model for analytics
    gold:
      +materialized: table
      +schema: gold
```

## 🎯 Business Value

### **Data Quality**
- **Automated Testing**: 5 comprehensive tests ensure data integrity
- **Deduplication**: 18% duplicate removal improves data quality
- **Validation**: Range checks and business rules enforcement
- **NULL Analysis**: Comprehensive analysis of NULL values and their business meaning

### **Analytics Ready**
- **Star Schema**: Optimized for business intelligence
- **Dimensional Model**: Easy to query and understand
- **Data Lineage**: Complete traceability from source to analytics
- **Documentation**: Self-documenting code with automated lineage

### **Scalability**
- **Production Ready**: S3 integration for cloud deployment
- **Modular Design**: Easy to extend with new data sources
- **Performance Optimized**: Sub-minute processing for 100K records
- **Modern Stack**: dbt + DuckDB + Apache Airflow

---

*This lineage visualization shows the complete data flow from raw Excel data to analytics-ready dimensional model, with full traceability and quality assurance.*
