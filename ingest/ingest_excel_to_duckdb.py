import argparse
import os
from pathlib import Path
import uuid
import pandas as pd
import duckdb
from datetime import datetime
import glob

try:
    import pyarrow as pa  # noqa: F401
    import pyarrow.parquet as pq
except Exception:
    pq = None

try:
    import boto3  # noqa: F401
except Exception:
    boto3 = None

parser = argparse.ArgumentParser(description='Excel to DuckDB ingestion with full refresh and incremental modes')
parser.add_argument('--excel', help='Path to source Excel file (single file)')
parser.add_argument('--excel_dir', help='Directory containing Excel files (incremental mode)')
parser.add_argument('--excel_pattern', help='Pattern to match Excel files (e.g., "*.xlsx")')
parser.add_argument('--duckdb', required=True, help='Path to destination DuckDB database')
parser.add_argument('--raw_dir', required=False, default='raw_data', help='Local directory for RAW layer (simulating S3)')
parser.add_argument('--table', required=False, default='raw_loans', help='Logical name for RAW table')
parser.add_argument('--mode', choices=['full_refresh', 'incremental'], default='full_refresh', 
                    help='Ingestion mode: full_refresh (replace all) or incremental (append new)')
parser.add_argument('--prod', action='store_true', help='If specified, upload Parquet files to S3')
parser.add_argument('--s3_bucket', required=False, default=os.getenv('RAW_S3_BUCKET', ''), help='S3 bucket for RAW data')
parser.add_argument('--s3_prefix', required=False, default=os.getenv('RAW_S3_PREFIX', 'raw/loans'), help='S3 prefix (folder)')
args = parser.parse_args()

def load_excel_files(excel_path=None, excel_dir=None, excel_pattern=None):
    """Load Excel files and return combined DataFrame"""
    dfs = []
    
    if excel_path:
        # Single file mode
        excel_path = Path(excel_path)
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        print(f"📖 Loading single Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        df['_source_file'] = excel_path.name
        df['_ingestion_timestamp'] = datetime.now()
        dfs.append(df)
        
    elif excel_dir:
        # Directory mode (incremental) - more flexible
        excel_dir = Path(excel_dir)
        if not excel_dir.exists():
            raise FileNotFoundError(f"Excel directory not found: {excel_dir}")
        
        # Use pattern if provided, otherwise default to all Excel files
        if excel_pattern:
            excel_files = list(excel_dir.glob(excel_pattern))
        else:
            excel_files = list(excel_dir.glob("*.xlsx")) + list(excel_dir.glob("*.xls"))
        
        if not excel_files:
            raise FileNotFoundError(f"No Excel files found in: {excel_dir} with pattern: {excel_pattern or '*.xlsx, *.xls'}")
        
        print(f"📖 Loading {len(excel_files)} Excel files from: {excel_dir}")
        for file_path in excel_files:
            print(f"  - Processing: {file_path.name}")
            df = pd.read_excel(file_path)
            df['_source_file'] = file_path.name
            df['_ingestion_timestamp'] = datetime.now()
            dfs.append(df)
    else:
        raise ValueError("Either --excel or --excel_dir must be specified")
    
    # Combine all DataFrames
    if len(dfs) == 1:
        return dfs[0]
    else:
        return pd.concat(dfs, ignore_index=True)

def write_parquet_with_metadata(df, raw_dir, table_name, mode):
    """Write DataFrame to Parquet with metadata"""
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp and mode
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parquet_filename = f"{table_name}_{mode}_{timestamp}_{uuid.uuid4().hex[:8]}.parquet"
    parquet_path = raw_dir / parquet_filename
    
    if pq is None:
        # Fallback using DuckDB to export Parquet
        tmp_con = duckdb.connect(database=':memory:')
        tmp_con.register('df_src', df)
        tmp_con.execute(f"COPY (SELECT * FROM df_src) TO '{parquet_path.as_posix()}' (FORMAT PARQUET);")
    else:
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_path)
    
    print(f"✅ RAW Parquet written: {parquet_path}")
    return parquet_path

def upload_to_s3(parquet_path, s3_bucket, s3_prefix):
    """Upload Parquet file to S3"""
    if boto3 is None:
        raise RuntimeError('boto3 not installed. Install boto3 or remove --prod')
    if not s3_bucket:
        raise ValueError('Missing --s3_bucket (or env RAW_S3_BUCKET) for --prod')
    
    s3 = boto3.client('s3')
    s3_key = f"{s3_prefix.rstrip('/')}/{parquet_path.name}"
    s3.upload_file(str(parquet_path), s3_bucket, s3_key)
    print(f"✅ Uploaded to S3: s3://{s3_bucket}/{s3_key}")

def load_to_duckdb(parquet_path, db_path, table_name, mode):
    """Load Parquet data to DuckDB with mode-specific logic"""
    con = duckdb.connect(database=str(db_path), read_only=False)
    con.execute('CREATE SCHEMA IF NOT EXISTS raw;')
    
    if mode == 'full_refresh':
        # Drop and recreate table
        con.execute(f'DROP TABLE IF EXISTS raw.{table_name};')
        con.execute(f"CREATE TABLE raw.{table_name} AS SELECT * FROM read_parquet('{parquet_path.as_posix()}');")
        print(f"✅ Full refresh: Recreated table raw.{table_name}")
        
    elif mode == 'incremental':
        # Check if table exists
        table_exists = con.execute(f"""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'raw' AND table_name = '{table_name}'
        """).fetchone()[0] > 0
        
        if not table_exists:
            # Create table if it doesn't exist
            con.execute(f"CREATE TABLE raw.{table_name} AS SELECT * FROM read_parquet('{parquet_path.as_posix()}');")
            print(f"✅ Incremental: Created new table raw.{table_name}")
        else:
            # Append to existing table
            con.execute(f"""
                INSERT INTO raw.{table_name} 
                SELECT * FROM read_parquet('{parquet_path.as_posix()}')
            """)
            print(f"✅ Incremental: Appended to existing table raw.{table_name}")
    
    # Get final count
    count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
    print(f"   Total records in raw.{table_name}: {count:,}")
    
    con.close()

# Main execution
db_path = Path(args.duckdb)
raw_dir = Path(args.raw_dir)
table_name = args.table

print(f"🚀 Starting {args.mode} ingestion")
print(f"   Mode: {args.mode}")
print(f"   Table: raw.{table_name}")
print(f"   Database: {db_path}")

# 1) Load Excel files
df = load_excel_files(args.excel, args.excel_dir, args.excel_pattern)
print(f"   Loaded {len(df):,} records from Excel")

# 2) Write RAW data to Parquet
parquet_path = write_parquet_with_metadata(df, raw_dir, table_name, args.mode)

# 3) Upload to S3 (if production mode)
if args.prod:
    upload_to_s3(parquet_path, args.s3_bucket, args.s3_prefix)

# 4) Load to DuckDB
load_to_duckdb(parquet_path, db_path, table_name, args.mode)

print("✅ Ingestion completed successfully")

