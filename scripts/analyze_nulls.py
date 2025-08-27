#!/usr/bin/env python3
"""
NULL Analysis Script - Detailed Meaning Analysis
"""

import duckdb
import pandas as pd
from pathlib import Path

def analyze_null_meanings():
    """Analyze what each NULL means in each column"""
    
    try:
        con = duckdb.connect('data_challenge.duckdb')
        print("✅ Connected to database successfully!")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("💡 Make sure DBeaver is not connected to the database")
        return
    
    print("\n🔍 DETAILED NULL MEANING ANALYSIS")
    print("=" * 70)
    
    # Analyze each column in raw.raw_loans
    print("\n📊 RAW.RAW_LOANS - NULL meaning by column:")
    print("=" * 70)
    
    raw_analysis = analyze_raw_nulls(con)
    
    # Analyze each column in silver.silver_loans
    print("\n📊 MAIN_SILVER.SILVER_LOANS - NULL meaning by column:")
    print("=" * 70)
    
    silver_analysis = analyze_silver_nulls(con)
    
    con.close()
    
    # Generar documentación detallada
    generate_detailed_null_documentation(raw_analysis, silver_analysis)

def analyze_raw_nulls(con):
    """Analyze NULLs in raw layer with detailed meaning"""
    
    columns_analysis = {
        'Loan ID': {
            'meaning': 'ERROR: Should not have NULLs - Unique identifier required',
            'impact': 'CRITICAL - Invalid record',
            'action': 'Review data source'
        },
        'Customer ID': {
            'meaning': 'ERROR: Should not have NULLs - Customer must be identified',
            'impact': 'CRITICAL - Invalid record',
            'action': 'Review data source'
        },
        'Loan Status': {
            'meaning': 'ERROR: Loan status is mandatory',
            'impact': 'CRITICAL - Cannot process',
            'action': 'Review data source'
        },
        'Term': {
            'meaning': 'Missing data - Loan term not specified',
            'impact': 'HIGH - Affects risk analysis',
            'action': 'Request complete data'
        },
        'Credit Score': {
            'meaning': 'No credit history or insufficient data',
            'impact': 'HIGH - Cannot assess credit risk',
            'action': 'Find alternative data sources'
        },
        'Current Loan Amount': {
            'meaning': 'No active loans or amount not reported',
            'impact': 'MEDIUM - Affects exposure analysis',
            'action': 'Verify if 0 or truly NULL'
        },
        'Annual Income': {
            'meaning': 'Unemployed or income not reported',
            'impact': 'HIGH - Cannot assess repayment capacity',
            'action': 'Request employment information'
        },
        'Monthly Debt': {
            'meaning': 'No monthly debt obligations',
            'impact': 'LOW - Positive for analysis',
            'action': 'Confirm if 0 or NULL'
        },
        'Years of Credit History': {
            'meaning': 'No established credit history',
            'impact': 'HIGH - New customer or no credit',
            'action': 'Evaluate as new customer'
        },
        'Months since last delinquent': {
            'meaning': 'NO DELINQUENCY - Clean history (POSITIVE)',
            'impact': 'POSITIVE - Good payment behavior',
            'action': 'Mark as good payer'
        },
        'Number of Open Accounts': {
            'meaning': 'No open accounts or data not available',
            'impact': 'MEDIUM - Affects credit diversification',
            'action': 'Verify if 0 or NULL'
        },
        'Number of Credit Problems': {
            'meaning': 'NO CREDIT PROBLEMS (POSITIVE)',
            'impact': 'POSITIVE - Good history',
            'action': 'Mark as good payer'
        },
        'Current Credit Balance': {
            'meaning': 'No current credit balance',
            'impact': 'LOW - No credit exposure',
            'action': 'Verify if 0 or NULL'
        },
        'Maximum Open Credit': {
            'meaning': 'No maximum credit line established',
            'impact': 'MEDIUM - Cannot assess capacity',
            'action': 'Request credit limit information'
        },
        'Bankruptcies': {
            'meaning': 'NO BANKRUPTCIES (POSITIVE)',
            'impact': 'POSITIVE - Good financial history',
            'action': 'Mark as good risk'
        },
        'Tax Liens': {
            'meaning': 'NO TAX LIENS (POSITIVE)',
            'impact': 'POSITIVE - Clean tax situation',
            'action': 'Mark as good payer'
        },
        'Purpose': {
            'meaning': 'Loan purpose not specified',
            'impact': 'MEDIUM - Affects purpose-based risk analysis',
            'action': 'Request purpose information'
        },
        'Job Tenure Years': {
            'meaning': 'Unemployed or tenure not reported',
            'impact': 'HIGH - Cannot assess employment stability',
            'action': 'Request employment information'
        },
        'Home Ownership': {
            'meaning': 'Home ownership status unknown',
            'impact': 'MEDIUM - Affects stability analysis',
            'action': 'Request property information'
        }
    }
    
    results = []
    
    for column, analysis in columns_analysis.items():
        # Contar NULLs
        result = con.execute(f'''
            SELECT 
                COUNT(*) as total_rows,
                COUNT(*) FILTER (WHERE "{column}" IS NULL) as null_count,
                ROUND(COUNT(*) FILTER (WHERE "{column}" IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
            FROM raw.raw_loans
        ''').fetchone()
        
        if result[1] > 0:  # Si hay NULLs
            results.append({
                'column': column,
                'total_rows': result[0],
                'null_count': result[1],
                'null_percentage': result[2],
                'meaning': analysis['meaning'],
                'impact': analysis['impact'],
                'action': analysis['action']
            })
    
    # Show results
    if results:
        print("\n| Column | Total | NULLs | % | Meaning | Impact | Action |")
        print("|--------|-------|-------|---|---------|--------|--------|")
        for r in results:
            print(f"| {r['column']} | {r['total_rows']:,} | {r['null_count']:,} | {r['null_percentage']}% | {r['meaning']} | {r['impact']} | {r['action']} |")
    else:
        print("✅ No NULLs found in RAW layer")
    
    return results

def analyze_silver_nulls(con):
    """Analyze NULLs in silver layer with detailed meaning"""
    
    columns_analysis = {
        'loan_id': {
            'meaning': 'ERROR: Should not have NULLs after cleaning',
            'impact': 'CRITICAL - Invalid record',
            'action': 'Review cleaning process'
        },
        'customer_id': {
            'meaning': 'ERROR: Customer must be identified',
            'impact': 'CRITICAL - Invalid record',
            'action': 'Review cleaning process'
        },
        'loan_status': {
            'meaning': 'ERROR: Loan status is mandatory',
            'impact': 'CRITICAL - Cannot process',
            'action': 'Review cleaning process'
        },
        'term': {
            'meaning': 'Missing data - Term not specified',
            'impact': 'HIGH - Affects risk analysis',
            'action': 'Request complete data'
        },
        'credit_score': {
            'meaning': 'No credit history or insufficient data',
            'impact': 'HIGH - Cannot assess credit risk',
            'action': 'Find alternative data sources'
        },
        'current_loan_amount': {
            'meaning': 'No active loans or amount not reported',
            'impact': 'MEDIUM - Affects exposure analysis',
            'action': 'Verify if 0 or truly NULL'
        },
        'annual_income': {
            'meaning': 'Unemployed or income not reported',
            'impact': 'HIGH - Cannot assess repayment capacity',
            'action': 'Request employment information'
        },
        'monthly_debt': {
            'meaning': 'No monthly debt obligations',
            'impact': 'LOW - Positive for analysis',
            'action': 'Confirm if 0 or NULL'
        },
        'years_credit_history': {
            'meaning': 'No established credit history',
            'impact': 'HIGH - New customer or no credit',
            'action': 'Evaluate as new customer'
        },
        'months_since_last_delinquent': {
            'meaning': 'NO DELINQUENCY - Clean history (POSITIVE)',
            'impact': 'POSITIVE - Good payment behavior',
            'action': 'Mark as good payer'
        },
        'n_open_accounts': {
            'meaning': 'No open accounts or data not available',
            'impact': 'MEDIUM - Affects credit diversification',
            'action': 'Verify if 0 or NULL'
        },
        'n_credit_problems': {
            'meaning': 'NO CREDIT PROBLEMS (POSITIVE)',
            'impact': 'POSITIVE - Good history',
            'action': 'Mark as good payer'
        },
        'current_credit_balance': {
            'meaning': 'No current credit balance',
            'impact': 'LOW - No credit exposure',
            'action': 'Verify if 0 or NULL'
        },
        'max_open_credit': {
            'meaning': 'No maximum credit line established',
            'impact': 'MEDIUM - Cannot assess capacity',
            'action': 'Request credit limit information'
        },
        'bankruptcies': {
            'meaning': 'NO BANKRUPTCIES (POSITIVE)',
            'impact': 'POSITIVE - Good financial history',
            'action': 'Mark as good risk'
        },
        'tax_liens': {
            'meaning': 'NO TAX LIENS (POSITIVE)',
            'impact': 'POSITIVE - Clean tax situation',
            'action': 'Mark as good payer'
        },
        'purpose_name': {
            'meaning': 'Loan purpose not specified',
            'impact': 'MEDIUM - Affects purpose-based risk analysis',
            'action': 'Request purpose information'
        },
        'job_tenure_years': {
            'meaning': 'Unemployed or tenure not reported',
            'impact': 'HIGH - Cannot assess employment stability',
            'action': 'Request employment information'
        },
        'home_ownership': {
            'meaning': 'Home ownership status unknown',
            'impact': 'MEDIUM - Affects stability analysis',
            'action': 'Request property information'
        }
    }
    
    results = []
    
    for column, analysis in columns_analysis.items():
        # Contar NULLs
        result = con.execute(f'''
            SELECT 
                COUNT(*) as total_rows,
                COUNT(*) FILTER (WHERE {column} IS NULL) as null_count,
                ROUND(COUNT(*) FILTER (WHERE {column} IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
            FROM main_silver.silver_loans
        ''').fetchone()
        
        if result[1] > 0:  # Si hay NULLs
            results.append({
                'column': column,
                'total_rows': result[0],
                'null_count': result[1],
                'null_percentage': result[2],
                'meaning': analysis['meaning'],
                'impact': analysis['impact'],
                'action': analysis['action']
            })
    
    # Show results
    if results:
        print("\n| Column | Total | NULLs | % | Meaning | Impact | Action |")
        print("|--------|-------|-------|---|---------|--------|--------|")
        for r in results:
            print(f"| {r['column']} | {r['total_rows']:,} | {r['null_count']:,} | {r['null_percentage']}% | {r['meaning']} | {r['impact']} | {r['action']} |")
    else:
        print("✅ No NULLs found in SILVER layer")
    
    return results

def generate_detailed_null_documentation(raw_analysis, silver_analysis):
    """Generate detailed documentation about NULL meanings"""
    
    docs_content = """# NULL Values - Detailed Meaning Analysis

## Overview
This document provides a detailed analysis of what each NULL value means in each column of our loan data pipeline.

## NULL Classification by Impact

### 🔴 CRÍTICO (Critical)
- **Definition**: NULLs that indicate data quality errors or missing mandatory information
- **Action Required**: Immediate investigation and data source review
- **Examples**: Loan ID, Customer ID, Loan Status

### 🟡 ALTO (High)
- **Definition**: NULLs that significantly impact business analysis and decision making
- **Action Required**: Data collection improvement or alternative data sources
- **Examples**: Credit Score, Annual Income, Years of Credit History

### 🟠 MEDIO (Medium)
- **Definition**: NULLs that affect specific analyses but don't prevent core operations
- **Action Required**: Monitor and improve data collection processes
- **Examples**: Purpose, Home Ownership, Maximum Open Credit

### 🟢 BAJO (Low)
- **Definition**: NULLs that have minimal impact on analysis
- **Action Required**: Verify if NULL is intentional (0 vs NULL)
- **Examples**: Monthly Debt, Current Credit Balance

### ✅ POSITIVO (Positive)
- **Definition**: NULLs that actually indicate good behavior or clean history
- **Action Required**: Use as positive indicators in analysis
- **Examples**: Months since last delinquent, Bankruptcies, Tax Liens

## Detailed NULL Analysis by Layer

### RAW Layer Analysis
"""
    
    if raw_analysis:
        docs_content += """
| Column | NULL Count | NULL % | Meaning | Impact | Action |
|--------|------------|--------|---------|--------|--------|
"""
        for r in raw_analysis:
            docs_content += f"| {r['column']} | {r['null_count']:,} | {r['null_percentage']}% | {r['meaning']} | {r['impact']} | {r['action']} |\n"
    else:
        docs_content += "✅ **No NULL values found in RAW layer**\n"
    
    docs_content += """

### SILVER Layer Analysis
"""
    
    if silver_analysis:
        docs_content += """
| Column | NULL Count | NULL % | Meaning | Impact | Action |
|--------|------------|--------|---------|--------|--------|
"""
        for r in silver_analysis:
            docs_content += f"| {r['column']} | {r['null_count']:,} | {r['null_percentage']}% | {r['meaning']} | {r['impact']} | {r['action']} |\n"
    else:
        docs_content += "✅ **No NULL values found in SILVER layer**\n"
    
    docs_content += """

## Business Rules for NULL Handling

### Credit-Related Fields

#### Credit Score
- **NULL Meaning**: No credit history or insufficient data
- **Business Impact**: Cannot assess credit risk
- **Handling Strategy**: 
  - Use alternative risk indicators
  - Mark as "New Customer" or "No Credit History"
  - Implement manual review process

#### Years of Credit History
- **NULL Meaning**: No established credit history
- **Business Impact**: Cannot assess credit experience
- **Handling Strategy**:
  - Categorize as "New to Credit"
  - Use other stability indicators
  - Apply higher risk premiums

#### Months since last delinquent
- **NULL Meaning**: **POSITIVE** - No delinquency history
- **Business Impact**: **POSITIVE** - Good payment behavior
- **Handling Strategy**:
  - Use as positive indicator
  - Mark as "Clean Payment History"
  - Apply favorable terms

### Financial Fields

#### Annual Income
- **NULL Meaning**: Unemployed or income not reported
- **Business Impact**: Cannot assess repayment capacity
- **Handling Strategy**:
  - Request employment verification
  - Use alternative income sources
  - Apply conservative underwriting

#### Monthly Debt
- **NULL Meaning**: No debt obligations
- **Business Impact**: **POSITIVE** - Lower debt burden
- **Handling Strategy**:
  - Verify if truly 0 or missing data
  - Use as positive indicator
  - Apply favorable debt-to-income ratios

#### Current Loan Amount
- **NULL Meaning**: No active loans or amount not reported
- **Business Impact**: Cannot assess current exposure
- **Handling Strategy**:
  - Verify if 0 or missing data
  - Check for other loan sources
  - Apply conservative exposure limits

### Employment Fields

#### Job Tenure Years
- **NULL Meaning**: Unemployed or tenure not reported
- **Business Impact**: Cannot assess employment stability
- **Handling Strategy**:
  - Request employment verification
  - Use alternative stability indicators
  - Apply higher risk assessment

#### Home Ownership
- **NULL Meaning**: Home ownership status unknown
- **Business Impact**: Cannot assess stability and commitment
- **Handling Strategy**:
  - Request property information
  - Use alternative stability measures
  - Apply neutral risk assessment

### Legal/Financial History Fields

#### Bankruptcies
- **NULL Meaning**: **POSITIVE** - No bankruptcy history
- **Business Impact**: **POSITIVE** - Good financial history
- **Handling Strategy**:
  - Use as positive indicator
  - Mark as "Clean Financial History"
  - Apply favorable terms

#### Tax Liens
- **NULL Meaning**: **POSITIVE** - No tax lien history
- **Business Impact**: **POSITIVE** - Good tax compliance
- **Handling Strategy**:
  - Use as positive indicator
  - Mark as "Good Tax Standing"
  - Apply favorable terms

## Data Quality Recommendations

### 1. Immediate Actions
- **Critical NULLs**: Investigate data source issues
- **High Impact NULLs**: Implement data collection improvements
- **Positive NULLs**: Leverage as business indicators

### 2. Monitoring
- Set up alerts for unexpected NULL patterns
- Track NULL rates over time
- Monitor impact on business metrics

### 3. Process Improvements
- Enhance data collection processes
- Implement validation rules
- Create alternative data sources

### 4. Business Intelligence
- Create NULL-aware dashboards
- Develop risk models that account for NULLs
- Build customer segmentation including NULL patterns

## Technical Implementation

### SQL Examples for NULL Handling

```sql
-- Example: Credit Score categorization
CASE 
    WHEN credit_score IS NULL THEN 'No Credit History'
    WHEN credit_score < 580 THEN 'Poor'
    WHEN credit_score < 670 THEN 'Fair'
    WHEN credit_score < 740 THEN 'Good'
    ELSE 'Excellent'
END as credit_score_category

-- Example: Positive NULL indicators
CASE 
    WHEN months_since_last_delinquent IS NULL THEN 'Clean History'
    WHEN months_since_last_delinquent > 24 THEN 'Good Standing'
    ELSE 'Recent Issues'
END as payment_history_category

-- Example: Risk assessment with NULLs
CASE 
    WHEN annual_income IS NULL AND job_tenure_years IS NULL THEN 'High Risk - No Income Data'
    WHEN annual_income IS NULL THEN 'Medium Risk - Income Missing'
    WHEN job_tenure_years IS NULL THEN 'Medium Risk - Employment Unknown'
    ELSE 'Standard Risk Assessment'
END as risk_category
```

### dbt Tests for NULL Validation

```yaml
# Example dbt tests
- name: critical_fields_not_null
  description: "Critical fields should not be NULL"
  tests:
    - not_null:
        where: "loan_status IS NOT NULL"

- name: positive_nulls_validation
  description: "Validate positive NULL patterns"
  tests:
    - dbt_utils.expression_is_true:
        expression: "months_since_last_delinquent IS NULL OR months_since_last_delinquent >= 0"

- name: null_pattern_consistency
  description: "Check NULL pattern consistency"
  tests:
    - dbt_utils.expression_is_true:
        expression: "(annual_income IS NULL AND job_tenure_years IS NULL) OR (annual_income IS NOT NULL OR job_tenure_years IS NOT NULL)"
```

---
*This document should be updated whenever NULL patterns change or new business rules are implemented.*
"""
    
    # Guardar documentación
    docs_path = Path(__file__).parent.parent / "docs" / "NULL_MEANING_ANALYSIS.md"
    with open(docs_path, 'w', encoding='utf-8') as f:
        f.write(docs_content)
    
    print(f"\n📄 Detailed documentation generated: {docs_path}")
    print("✅ Complete NULL meaning analysis completed")

if __name__ == "__main__":
    analyze_null_meanings()
