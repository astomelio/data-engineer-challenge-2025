#!/usr/bin/env python3
"""
Script to demonstrate different ingestion modes:
- Full refresh: Replace all data
- Incremental: Append new data from Excel files in data directory
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ SUCCESS")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main function to demonstrate ingestion modes"""
    
    # Get project paths
    project_root = Path(__file__).parent.parent
    ingest_script = project_root / "ingest" / "ingest_excel_to_duckdb.py"
    excel_file = project_root / "data" / "Data Engineer Challenge.xlsx"
    excel_dir = project_root / "data"  # Same directory for both modes
    duckdb_path = project_root / "dbt" / "data_challenge.duckdb"
    raw_dir = project_root / "raw_data"
    
    print("📊 Loan Data Pipeline - Ingestion Modes Demo")
    print("=" * 60)
    
    # Check if files exist
    if not ingest_script.exists():
        print(f"❌ Ingestion script not found: {ingest_script}")
        sys.exit(1)
    
    if not excel_file.exists():
        print(f"❌ Excel file not found: {excel_file}")
        sys.exit(1)
    
    print(f"✅ Ingestion script: {ingest_script}")
    print(f"✅ Excel file: {excel_file}")
    print(f"✅ Excel directory: {excel_dir}")
    print(f"✅ DuckDB path: {duckdb_path}")
    print(f"✅ Raw directory: {raw_dir}")
    
    # Mode 1: Full Refresh
    print("\n" + "=" * 60)
    print("🔄 MODE 1: FULL REFRESH")
    print("=" * 60)
    print("This mode will:")
    print("- Replace all existing data in raw.raw_loans")
    print("- Process the main Excel file")
    print("- Create a fresh RAW layer")
    print("- Use: --excel (single file)")
    
    cmd_full_refresh = [
        "python", str(ingest_script),
        "--excel", str(excel_file),
        "--duckdb", str(duckdb_path),
        "--raw_dir", str(raw_dir),
        "--mode", "full_refresh"
    ]
    
    success_full = run_command(cmd_full_refresh, "Full Refresh Ingestion")
    
    if not success_full:
        print("❌ Full refresh failed. Stopping demo.")
        sys.exit(1)
    
    # Mode 2: Incremental
    print("\n" + "=" * 60)
    print("➕ MODE 2: INCREMENTAL")
    print("=" * 60)
    print("This mode will:")
    print("- Append new data to existing raw.raw_loans")
    print("- Process all Excel files in the data directory")
    print("- Add metadata columns (_source_file, _ingestion_timestamp)")
    print("- Use: --excel_dir (directory) + --excel_pattern (optional)")
    print("\n💡 Note: Since we only have one Excel file, this will just append the same data")
    
    cmd_incremental = [
        "python", str(ingest_script),
        "--excel_dir", str(excel_dir),
        "--duckdb", str(duckdb_path),
        "--raw_dir", str(raw_dir),
        "--mode", "incremental"
    ]
    
    success_incremental = run_command(cmd_incremental, "Incremental Ingestion")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    print(f"Full Refresh: {'✅ SUCCESS' if success_full else '❌ FAILED'}")
    print(f"Incremental:  {'✅ SUCCESS' if success_incremental else '❌ FAILED'}")
    
    if success_full and success_incremental:
        print("\n🎉 Both modes completed successfully!")
        print("\n💡 Usage Tips:")
        print("- Use 'full_refresh' for initial load or complete data replacement")
        print("- Use 'incremental' for daily updates with new Excel files")
        print("- Just add new Excel files to the data/ directory (no special folders needed)")
        print("- Use --excel_pattern to process only specific files (e.g., 'new_*.xlsx')")
        print("- Check raw_data/ directory for Parquet files with timestamps")
    else:
        print("\n⚠️  Some modes failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
