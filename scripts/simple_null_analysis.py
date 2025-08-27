#!/usr/bin/env python3
"""
Simple NULL Analysis Script
"""

import duckdb
import pandas as pd

def analyze_nulls_simple():
    """Simple analysis of NULL values"""
    
    try:
        con = duckdb.connect('dbt/data_challenge.duckdb')
        print("✅ Connected to database successfully!")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return
    
    print("\n🔍 SIMPLE NULL ANALYSIS")
    print("=" * 50)
    
    # Analyze raw.raw_loans
    print("\n📊 RAW.RAW_LOANS - NULL Analysis:")
    print("-" * 40)
    
    # Get columns from raw.raw_loans
    columns = con.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'raw' AND table_name = 'raw_loans'
        ORDER BY ordinal_position
    """).fetchall()
    
    print("Columns found:")
    for col in columns:
        print(f"  - {col[0]}")
    
    # Analyze NULLs in each column
    print("\nNULL Analysis:")
    for col in columns:
        column_name = col[0]
        try:
            result = con.execute(f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(*) FILTER (WHERE "{column_name}" IS NULL) as null_count,
                    ROUND(COUNT(*) FILTER (WHERE "{column_name}" IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
                FROM raw.raw_loans
            """).fetchone()
            
            if result[1] > 0:  # If there are NULLs
                print(f"  {column_name}: {result[1]:,} NULLs ({result[2]}%) of {result[0]:,} total")
        except Exception as e:
            print(f"  Error in {column_name}: {e}")
    
    # Analyze silver.silver_loans
    print("\n📊 MAIN_SILVER.SILVER_LOANS - NULL Analysis:")
    print("-" * 40)
    
    # Get columns from silver.silver_loans
    columns_silver = con.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'main_silver' AND table_name = 'silver_loans'
        ORDER BY ordinal_position
    """).fetchall()
    
    print("Columns found:")
    for col in columns_silver:
        print(f"  - {col[0]}")
    
    # Analyze NULLs in each column
    print("\nNULL Analysis:")
    for col in columns_silver:
        column_name = col[0]
        try:
            result = con.execute(f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(*) FILTER (WHERE {column_name} IS NULL) as null_count,
                    ROUND(COUNT(*) FILTER (WHERE {column_name} IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
                FROM main_silver.silver_loans
            """).fetchone()
            
            if result[1] > 0:  # If there are NULLs
                print(f"  {column_name}: {result[1]:,} NULLs ({result[2]}%) of {result[0]:,} total")
        except Exception as e:
            print(f"  Error in {column_name}: {e}")
    
    con.close()
    print("\n✅ Analysis completed")

if __name__ == "__main__":
    analyze_nulls_simple()
