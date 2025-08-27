#!/usr/bin/env python3
"""
Interactive script to explore the DuckDB database from the data pipeline.
"""

import duckdb
import sys
from pathlib import Path

def connect_db():
    """Connect to DuckDB database"""
    db_path = Path(__file__).parent.parent / "dbt" / "data_challenge.duckdb"
    return duckdb.connect(str(db_path))

def show_summary(con):
    """Show general database summary"""
    print("=" * 60)
    print("📊 DATABASE SUMMARY")
    print("=" * 60)
    
    # Counts by layer
    raw_count = con.execute("SELECT COUNT(*) FROM raw.raw_loans").fetchone()[0]
    silver_count = con.execute("SELECT COUNT(*) FROM main_silver.silver_loans").fetchone()[0]
    fact_count = con.execute("SELECT COUNT(*) FROM main_gold.fact_loan").fetchone()[0]
    customer_count = con.execute("SELECT COUNT(*) FROM main_gold.dim_customer").fetchone()[0]
    purpose_count = con.execute("SELECT COUNT(*) FROM main_gold.dim_purpose").fetchone()[0]
    
    print(f"🔴 RAW Layer: {raw_count:,} records")
    print(f"🟡 SILVER Layer: {silver_count:,} records (after deduplication)")
    print(f"🟢 GOLD Layer:")
    print(f"   - Fact Table: {fact_count:,} records")
    print(f"   - Dim Customer: {customer_count:,} unique customers")
    print(f"   - Dim Purpose: {purpose_count} unique purposes")
    
    # Loan status statistics
    loan_status = con.execute("""
        SELECT loan_status, COUNT(*) as count, 
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM main_gold.fact_loan 
        GROUP BY loan_status
    """).fetchall()
    
    print(f"\n📈 Loan Status:")
    for status, count, pct in loan_status:
        print(f"   - {status}: {count:,} ({pct}%)")

def show_purpose_analysis(con):
    """Loan purpose analysis"""
    print("\n" + "=" * 60)
    print("🎯 LOAN PURPOSE ANALYSIS")
    print("=" * 60)
    
    purposes = con.execute("""
        SELECT p.purpose_name, COUNT(*) as count,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM main_gold.fact_loan f 
        JOIN main_gold.dim_purpose p ON f.purpose_id = p.purpose_id 
        GROUP BY p.purpose_name 
        ORDER BY count DESC
    """).fetchall()
    
    for purpose, count, pct in purposes:
        print(f"   - {purpose}: {count:,} ({pct}%)")

def show_credit_analysis(con):
    """Credit score analysis"""
    print("\n" + "=" * 60)
    print("💳 CREDIT SCORE ANALYSIS")
    print("=" * 60)
    
    credit_stats = con.execute("""
        SELECT 
            AVG(credit_score) as avg_score,
            MIN(credit_score) as min_score,
            MAX(credit_score) as max_score,
            STDDEV(credit_score) as std_score
        FROM main_gold.fact_loan
        WHERE credit_score IS NOT NULL
    """).fetchall()[0]
    
    avg_score, min_score, max_score, std_score = credit_stats
    print(f"   - Average: {avg_score:.1f}")
    print(f"   - Minimum: {min_score}")
    print(f"   - Maximum: {max_score}")
    print(f"   - Standard deviation: {std_score:.1f}")
    
    # Credit score distribution
    credit_dist = con.execute("""
        SELECT 
            CASE 
                WHEN credit_score < 580 THEN 'Poor (<580)'
                WHEN credit_score < 670 THEN 'Fair (580-669)'
                WHEN credit_score < 740 THEN 'Good (670-739)'
                WHEN credit_score < 800 THEN 'Very Good (740-799)'
                ELSE 'Excellent (800+)'
            END as credit_category,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM main_gold.fact_loan
        WHERE credit_score IS NOT NULL
        GROUP BY 1
        ORDER BY MIN(credit_score)
    """).fetchall()
    
    print(f"\n📊 Credit Score Distribution:")
    for category, count, pct in credit_dist:
        print(f"   - {category}: {count:,} ({pct}%)")

def show_income_analysis(con):
    """Annual income analysis"""
    print("\n" + "=" * 60)
    print("💰 ANNUAL INCOME ANALYSIS")
    print("=" * 60)
    
    income_stats = con.execute("""
        SELECT 
            AVG(annual_income) as avg_income,
            MIN(annual_income) as min_income,
            MAX(annual_income) as max_income,
            STDDEV(annual_income) as std_income
        FROM main_gold.fact_loan
        WHERE annual_income IS NOT NULL
    """).fetchall()[0]
    
    avg_income, min_income, max_income, std_income = income_stats
    print(f"   - Average: ${avg_income:,.0f}")
    print(f"   - Minimum: ${min_income:,.0f}")
    print(f"   - Maximum: ${max_income:,.0f}")
    print(f"   - Standard deviation: ${std_income:,.0f}")

def show_home_ownership_analysis(con):
    """Home ownership analysis"""
    print("\n" + "=" * 60)
    print("🏠 HOME OWNERSHIP ANALYSIS")
    print("=" * 60)
    
    home_ownership = con.execute("""
        SELECT home_ownership, COUNT(*) as count,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM main_gold.dim_customer
        GROUP BY home_ownership
        ORDER BY count DESC
    """).fetchall()
    
    for ownership, count, pct in home_ownership:
        print(f"   - {ownership}: {count:,} ({pct}%)")

def show_null_analysis(con):
    """NULL values analysis"""
    print("\n" + "=" * 60)
    print("🔍 NULL VALUES ANALYSIS")
    print("=" * 60)
    
    # Key fields with NULL analysis
    null_fields = [
        'credit_score', 'annual_income', 'job_tenure_years', 
        'months_since_last_delinquent', 'bankruptcies', 'tax_liens'
    ]
    
    for field in null_fields:
        result = con.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE {field} IS NULL) as null_count,
                ROUND(COUNT(*) FILTER (WHERE {field} IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
            FROM main_gold.fact_loan
        """).fetchone()
        
        total, null_count, null_pct = result
        print(f"   - {field}: {null_count:,} NULLs ({null_pct}%) of {total:,} total")

def show_sample_data(con):
    """Show sample data from each layer"""
    print("\n" + "=" * 60)
    print("📋 SAMPLE DATA")
    print("=" * 60)
    
    print("\n🔴 RAW Layer Sample (first 3 records):")
    raw_sample = con.execute("SELECT * FROM raw.raw_loans LIMIT 3").fetchall()
    for row in raw_sample:
        print(f"   {row}")
    
    print("\n🟡 SILVER Layer Sample (first 3 records):")
    silver_sample = con.execute("SELECT * FROM main_silver.silver_loans LIMIT 3").fetchall()
    for row in silver_sample:
        print(f"   {row}")
    
    print("\n🟢 GOLD Layer Sample (first 3 records):")
    gold_sample = con.execute("SELECT * FROM main_gold.fact_loan LIMIT 3").fetchall()
    for row in gold_sample:
        print(f"   {row}")

def main():
    """Main function"""
    try:
        con = connect_db()
        print("🚀 DuckDB Database Explorer")
        print("Database: data_challenge.duckdb")
        
        show_summary(con)
        show_purpose_analysis(con)
        show_credit_analysis(con)
        show_income_analysis(con)
        show_home_ownership_analysis(con)
        show_null_analysis(con)
        show_sample_data(con)
        
        con.close()
        print("\n✅ Database exploration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()