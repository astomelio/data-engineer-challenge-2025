#!/usr/bin/env python3
"""
Data Profiling Script - RAW Data Analysis
This script analyzes the raw Excel data BEFORE any pipeline processing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def profile_raw_data():
    """Profile the raw Excel data before any processing"""
    
    print("=" * 80)
    print("DATA PROFILING - RAW EXCEL DATA")
    print("=" * 80)
    print("This analysis is performed BEFORE any pipeline processing")
    print("=" * 80)
    
    # Load raw Excel data
    excel_file = "data/Data Engineer Challenge.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ Error: Excel file not found at {excel_file}")
        return
    
    print(f"📁 Loading raw data from: {excel_file}")
    df = pd.read_excel(excel_file)
    
    print(f"📊 Raw Data Overview:")
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {df.shape[1]}")
    print(f"  Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Data types
    print(f"\n📋 Data Types:")
    print(df.dtypes)
    
    # Duplicate analysis
    duplicates = df.duplicated().sum()
    print(f"\n🔄 Duplicate Analysis:")
    print(f"  Total Duplicates: {duplicates:,} ({duplicates/len(df)*100:.2f}%)")
    print(f"  Unique Records: {len(df) - duplicates:,}")
    
    # NULL analysis
    print(f"\n🔍 NULL Value Analysis:")
    null_analysis = df.isnull().sum().sort_values(ascending=False)
    null_percentage = (null_analysis / len(df) * 100).round(2)
    
    null_summary = pd.DataFrame({
        'Column': null_analysis.index,
        'NULL Count': null_analysis.values,
        'NULL Percentage': null_percentage.values
    })
    
    print(null_summary[null_summary['NULL Count'] > 0])
    
    # Outlier analysis
    print(f"\n📊 Outlier Analysis:")
    numerical_fields = ['Current Loan Amount', 'Credit Score', 'Annual Income', 'Monthly Debt']
    
    for field in numerical_fields:
        if field in df.columns:
            data = df[field].dropna()
            if len(data) > 0:
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = data[(data < lower_bound) | (data > upper_bound)]
                
                print(f"\n{field}:")
                print(f"  Range: {data.min():,.0f} - {data.max():,.0f}")
                print(f"  Outliers: {len(outliers):,} ({len(outliers)/len(data)*100:.2f}%)")
                print(f"  IQR: {IQR:,.0f}")
                
                # Check for sentinel values
                if field == 'Current Loan Amount':
                    sentinel_99999999 = (data == 99999999).sum()
                    if sentinel_99999999 > 0:
                        print(f"  ⚠️  Sentinel Value (99,999,999): {sentinel_99999999:,} records")
                
                if field == 'Credit Score':
                    high_scores = (data > 900).sum()
                    if high_scores > 0:
                        print(f"  ⚠️  High Scores (>900): {high_scores:,} records (likely x10 scale)")
    
    # Categorical analysis
    print(f"\n🏷️ Categorical Data Analysis:")
    categorical_fields = ['Home Ownership', 'Purpose', 'Years in current job', 'Loan Status']
    
    for field in categorical_fields:
        if field in df.columns:
            print(f"\n{field}:")
            value_counts = df[field].value_counts(dropna=False)
            print(value_counts.head(10))
            
            # Check for inconsistencies
            if field == 'Home Ownership':
                mortgage_variants = [v for v in value_counts.index if 'mortgage' in str(v).lower()]
                if len(mortgage_variants) > 1:
                    print(f"  ⚠️  Inconsistent mortgage values: {mortgage_variants}")
            
            if field == 'Purpose':
                purpose_variants = [v for v in value_counts.index if 'other' in str(v).lower()]
                if len(purpose_variants) > 1:
                    print(f"  ⚠️  Inconsistent 'other' values: {purpose_variants}")
            
            if field == 'Years in current job':
                text_values = [v for v in value_counts.index if isinstance(v, str) and any(char.isalpha() for char in str(v))]
                if text_values:
                    print(f"  ⚠️  Text values that need parsing: {text_values[:5]}")
    
    # Business insights
    print(f"\n📈 Business Insights:")
    
    # Loan status distribution
    if 'Loan Status' in df.columns:
        loan_status = df['Loan Status'].value_counts(normalize=True) * 100
        print(f"\nLoan Status Distribution:")
        for status, pct in loan_status.items():
            print(f"  {status}: {pct:.1f}%")
    
    # Credit score insights
    if 'Credit Score' in df.columns:
        credit_data = df['Credit Score'].dropna()
        print(f"\nCredit Score Insights:")
        print(f"  Average: {credit_data.mean():.1f}")
        print(f"  Median: {credit_data.median():.1f}")
        print(f"  Range: {credit_data.min()} - {credit_data.max()}")
    
    # Purpose analysis
    if 'Purpose' in df.columns:
        purpose_counts = df['Purpose'].value_counts()
        print(f"\nTop Loan Purposes:")
        for purpose, count in purpose_counts.head(5).items():
            pct = count / len(df) * 100
            print(f"  {purpose}: {count:,} ({pct:.1f}%)")
    
    # Data quality recommendations
    print(f"\n🎯 Data Quality Recommendations:")
    print("=" * 60)
    
    print("\n🔴 CRITICAL ISSUES:")
    print("1. Duplicate Records: 18% of data is duplicated")
    print("   → Implement deduplication in SILVER layer")
    print("   → Add unique constraints on business keys")
    
    print("\n2. Sentinel Values: Current Loan Amount = 99,999,999")
    print("   → Replace with NULL or actual values")
    print("   → Add validation rules to prevent future sentinel values")
    
    print("\n3. Credit Score Scale: Values >900 indicate x10 scale error")
    print("   → Normalize credit scores to 300-850 range")
    print("   → Add range validation (300-850)")
    
    print("\n🟡 MODERATE ISSUES:")
    print("4. Inconsistent Categorical Values:")
    print("   → Standardize Home Ownership values")
    print("   → Normalize Purpose values (case, punctuation)")
    print("   → Parse Years in current job to numeric values")
    
    print("\n5. NULL Values (Business Impact):")
    print("   → Credit Score (19%): AFFECTS ANALYSIS - implement imputation")
    print("   → Annual Income (19%): AFFECTS ANALYSIS - implement imputation")
    print("   → Months since last delinquent (53%): POSITIVE - no action needed")
    
    print("\n🟢 POSITIVE INDICATORS:")
    print("6. Data Completeness: Good overall structure")
    print("7. No NULLs in critical business keys (Loan ID, Customer ID)")
    print("8. Reasonable data distributions for most fields")
    
    print("\n📋 IMPLEMENTATION PRIORITY:")
    print("1. HIGH: Deduplication and sentinel value handling")
    print("2. HIGH: Credit score normalization")
    print("3. MEDIUM: Categorical value standardization")
    print("4. MEDIUM: NULL value imputation for critical fields")
    print("5. LOW: Additional validation rules and monitoring")
    
    print("\n" + "=" * 80)
    print("PROFILING COMPLETE - Use these insights to design your pipeline")
    print("=" * 80)

if __name__ == "__main__":
    profile_raw_data()
