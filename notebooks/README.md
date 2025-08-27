# Data Profiling Notebooks

This directory contains Jupyter notebooks for data analysis and profiling.

## Files

### `profiling.ipynb`
**Data Profiling Analysis**

This notebook analyzes the loan dataset to understand data quality and inform pipeline design.

#### Features:
- **Data Loading**: Connects to DuckDB and loads RAW and SILVER layers
- **Duplicate Analysis**: Identifies and visualizes duplicate records
- **NULL Value Analysis**: Analysis with business impact classification
- **Outlier Detection**: Identifies sentinel values and scale errors
- **Business Insights**: Generates actionable business insights
- **Quality Recommendations**: Provides improvement recommendations
- **Performance Analysis**: Compares RAW vs SILVER layer improvements

#### Key Insights:
- **18% duplicate rate** requiring deduplication
- **Sentinel values** (99,999,999) in loan amounts
- **Credit score scale errors** (>900 values)
- **Categorical inconsistencies** in home ownership and purpose
- **NULL classification** by business impact (Missing Data, Not Applicable, etc.)

#### Usage:
```bash
# Navigate to notebooks directory
cd notebooks

# Start Jupyter
jupyter notebook

# Open profiling.ipynb
# Run all cells sequentially
```

#### Requirements:
- Python 3.8+
- Jupyter Notebook
- Required packages: pandas, numpy, matplotlib, seaborn, duckdb

#### Output:
- Data quality report
- Visualizations for key metrics
- Business insights and recommendations
- Pipeline performance analysis

---

## Purpose

This notebook demonstrates the **data profiling phase** that informed the design of our data pipeline:

1. **Before Pipeline Design**: Understanding data quality issues
2. **During Development**: Validating transformations
3. **After Implementation**: Measuring pipeline success

## Key Metrics Analyzed

### Data Quality
- Duplicate rates
- NULL value patterns
- Outlier detection
- Data type consistency

### Business Metrics
- Loan status distribution
- Credit score analysis
- Purpose categorization
- Home ownership patterns

### Pipeline Performance
- Deduplication effectiveness
- Data completeness
- Validation results
- Processing efficiency

---

*This profiling analysis directly informed the design of our RAW → SILVER → GOLD architecture and ensured data quality throughout the pipeline.*
