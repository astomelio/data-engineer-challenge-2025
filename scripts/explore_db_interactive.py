#!/usr/bin/env python3
"""
Interactive Database Explorer for DuckDB
"""

import duckdb
import pandas as pd
from pathlib import Path

def connect_db():
    """Connect to DuckDB database"""
    db_path = Path(__file__).parent.parent / "dbt" / "data_challenge.duckdb"
    return duckdb.connect(str(db_path))

def show_schemas_and_tables(con):
    """Show all schemas and tables"""
    print("📊 DATABASE SCHEMAS AND TABLES")
    print("=" * 50)
    
    # Get schemas
    schemas = con.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')").fetchall()
    print("Schemas:")
    for schema in schemas:
        print(f"  - {schema[0]}")
    
    print("\nTables:")
    tables = con.execute("""
        SELECT table_schema, table_name, 
               (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
        FROM information_schema.tables t 
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
    """).fetchall()
    
    for schema, table, cols in tables:
        print(f"  - {schema}.{table} ({cols} columns)")

def show_table_info(con, schema, table):
    """Show detailed information about a table"""
    print(f"\n📋 DETAILS: {schema}.{table}")
    print("=" * 50)
    
    # Get row count
    count = con.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]
    print(f"Total rows: {count:,}")
    
    # Get column info
    columns = con.execute(f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_schema = '{schema}' AND table_name = '{table}'
        ORDER BY ordinal_position
    """).fetchall()
    
    print(f"\nColumns ({len(columns)}):")
    for col, dtype, nullable in columns:
        print(f"  - {col}: {dtype} {'(NULL)' if nullable == 'YES' else '(NOT NULL)'}")
    
    # Show sample data
    print(f"\nSample data (first 5 rows):")
    sample = con.execute(f"SELECT * FROM {schema}.{table} LIMIT 5").fetchdf()
    print(sample.to_string(index=False))

def interactive_menu():
    """Interactive menu for database exploration"""
    con = connect_db()
    
    while True:
        print("\n" + "=" * 60)
        print("🔍 DUCKDB DATABASE EXPLORER")
        print("=" * 60)
        print("1. Show all schemas and tables")
        print("2. Explore raw.raw_loans")
        print("3. Explore main_silver.silver_loans")
        print("4. Explore main_gold.fact_loan")
        print("5. Explore main_gold.dim_customer")
        print("6. Explore main_gold.dim_purpose")
        print("7. Custom query")
        print("0. Exit")
        
        choice = input("\nSelect option (0-7): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            show_schemas_and_tables(con)
        elif choice == "2":
            show_table_info(con, "raw", "raw_loans")
        elif choice == "3":
            show_table_info(con, "main_silver", "silver_loans")
        elif choice == "4":
            show_table_info(con, "main_gold", "fact_loan")
        elif choice == "5":
            show_table_info(con, "main_gold", "dim_customer")
        elif choice == "6":
            show_table_info(con, "main_gold", "dim_purpose")
        elif choice == "7":
            custom_query(con)
        else:
            print("❌ Invalid option. Please try again.")

def custom_query(con):
    """Execute custom SQL query"""
    print("\n🔧 CUSTOM SQL QUERY")
    print("=" * 50)
    print("Available tables:")
    print("- raw.raw_loans")
    print("- main_silver.silver_loans")
    print("- main_gold.fact_loan")
    print("- main_gold.dim_customer")
    print("- main_gold.dim_purpose")
    
    query = input("\nEnter your SQL query: ").strip()
    
    if not query:
        return
    
    try:
        result = con.execute(query).fetchdf()
        print(f"\n✅ Query executed successfully ({len(result)} rows):")
        print(result.to_string(index=False))
    except Exception as e:
        print(f"❌ Error executing query: {e}")

def main():
    """Main function"""
    print("🚀 DuckDB Database Explorer")
    print("Database: data_challenge.duckdb")
    
    try:
        # Test connection
        con = connect_db()
        print("✅ Database connected successfully!")
        con.close()
        
        # Start interactive menu
        interactive_menu()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure the pipeline has been run and the database file exists.")

if __name__ == "__main__":
    main()
