#!/usr/bin/env python3
"""
Local pipeline runner - executes the loan data pipeline without Airflow.
Uses the same functions from airflow/utils for consistency.
"""

import sys
import os
from pathlib import Path

# Add airflow/utils to path so we can import the functions
sys.path.append(str(Path(__file__).parent / "airflow" / "utils"))

from pipeline_functions import (
    run_ingestion,
    run_dbt_deps,
    run_dbt_models,
    run_dbt_tests,
    generate_dbt_docs,
    validate_data_quality,
    get_project_paths
)

def run_pipeline():
    """Run the complete pipeline locally."""
    print("🚀 Starting Loan Data Pipeline...")
    print("=" * 50)
    
    try:
        # Step 1: Ingestion
        print("\n📥 Step 1: Ingesting Excel to RAW...")
        run_ingestion()
        
        # Step 2: dbt deps
        print("\n📦 Step 2: Installing dbt dependencies...")
        run_dbt_deps()
        
        # Step 3: dbt run
        print("\n🔄 Step 3: Running dbt models (SILVER & GOLD)...")
        run_dbt_models()
        
        # Step 4: dbt tests
        print("\n🧪 Step 4: Running dbt tests...")
        run_dbt_tests()
        
        # Step 5: Data quality validation
        print("\n✅ Step 5: Additional data quality checks...")
        validate_data_quality()
        
        # Step 6: Generate docs
        print("\n📚 Step 6: Generating dbt documentation...")
        generate_dbt_docs()
        
        print("\n" + "=" * 50)
        print("🎉 Pipeline completed successfully!")
        print("\n📊 Data is now available in:")
        paths = get_project_paths()
        print(f"   - RAW: {paths['raw_dir']}")
        print(f"   - DuckDB: {paths['duckdb_path']}")
        print(f"   - dbt docs: {paths['dbt_dir']}/target/")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()

