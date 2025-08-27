"""
Pipeline utility functions for Airflow DAGs.
Contains all the business logic for the loan data pipeline.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any


def get_project_paths() -> Dict[str, Path]:
    """Get all project paths relative to the current working directory."""
    # Get the project root (2 levels up from airflow/utils)
    project_root = Path(__file__).parent.parent.parent
    return {
        "project_root": project_root,
        "excel_path": project_root / "data" / "Data Engineer Challenge.xlsx",
        "excel_dir": project_root / "data",  # Directory for incremental mode (same as main data dir)
        "duckdb_path": project_root / "dbt" / "data_challenge.duckdb",
        "raw_dir": project_root / "raw_data",
        "dbt_dir": project_root / "dbt",
        "ingest_script": project_root / "ingest" / "ingest_excel_to_duckdb.py"
    }


def run_ingestion(**context) -> bool:
    """Run the ingestion step: Excel → RAW (Parquet + DuckDB)"""
    paths = get_project_paths()
    
    try:
        # Get ingestion mode from context or environment
        ingestion_mode = context.get('params', {}).get('mode', os.getenv('INGESTION_MODE', 'full_refresh'))
        
        cmd = [
            "python", str(paths["ingest_script"]),
            "--duckdb", str(paths["duckdb_path"]),
            "--raw_dir", str(paths["raw_dir"]),
            "--mode", ingestion_mode,
        ]
        
        # Add source (single file or directory)
        if ingestion_mode == 'incremental':
            cmd.extend(["--excel_dir", str(paths["excel_dir"])])
        else:
            cmd.extend(["--excel", str(paths["excel_path"])])
        
        # Add S3 upload if in production
        if os.getenv('ENVIRONMENT') == 'production':
            s3_bucket = os.getenv('RAW_S3_BUCKET')
            s3_prefix = os.getenv('RAW_S3_PREFIX', 'raw/loans')
            if s3_bucket:
                cmd.extend(['--prod', '--s3_bucket', s3_bucket, '--s3_prefix', s3_prefix])
        
        print(f"🚀 Running ingestion in {ingestion_mode} mode")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Ingestion completed successfully")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ingestion failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise


def run_dbt_deps(**context) -> bool:
    """Install dbt dependencies"""
    paths = get_project_paths()
    
    try:
        cmd = ["dbt", "deps"]
        result = subprocess.run(cmd, cwd=str(paths["dbt_dir"]), capture_output=True, text=True, check=True)
        print("✅ dbt deps completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ dbt deps failed: {e}")
        raise


def run_dbt_models(**context) -> bool:
    """Run dbt models (SILVER and GOLD layers)"""
    paths = get_project_paths()
    
    try:
        cmd = ["dbt", "run"]
        result = subprocess.run(cmd, cwd=str(paths["dbt_dir"]), capture_output=True, text=True, check=True)
        print("✅ dbt run completed successfully")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ dbt run failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise


def run_dbt_tests(**context) -> bool:
    """Run dbt tests to validate data quality"""
    paths = get_project_paths()
    
    try:
        cmd = ["dbt", "test"]
        result = subprocess.run(cmd, cwd=str(paths["dbt_dir"]), capture_output=True, text=True, check=True)
        print("✅ dbt tests completed successfully")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ dbt tests failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise


def generate_dbt_docs(**context) -> bool:
    """Generate dbt documentation"""
    paths = get_project_paths()
    
    try:
        cmd = ["dbt", "docs", "generate"]
        result = subprocess.run(cmd, cwd=str(paths["dbt_dir"]), capture_output=True, text=True, check=True)
        print("✅ dbt docs generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ dbt docs generation failed: {e}")
        raise


def validate_data_quality(**context) -> bool:
    """Additional data quality checks beyond dbt tests"""
    paths = get_project_paths()
    
    try:
        # Example: Check if tables have data
        import duckdb
        
        con = duckdb.connect(str(paths["duckdb_path"]))
        
        # Check row counts
        raw_count = con.execute("SELECT COUNT(*) FROM raw.raw_loans").fetchone()[0]
        silver_count = con.execute("SELECT COUNT(*) FROM silver.silver_loans").fetchone()[0]
        gold_count = con.execute("SELECT COUNT(*) FROM gold.fact_loan").fetchone()[0]
        
        print(f"📊 Data counts: RAW={raw_count}, SILVER={silver_count}, GOLD={gold_count}")
        
        # Basic validation
        if raw_count == 0:
            raise ValueError("RAW layer is empty")
        if silver_count == 0:
            raise ValueError("SILVER layer is empty")
        if gold_count == 0:
            raise ValueError("GOLD layer is empty")
            
        print("✅ Data quality validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Data quality validation failed: {e}")
        raise

