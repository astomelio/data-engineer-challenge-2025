import argparse
import os
import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: str | None = None) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run end-to-end pipeline: ingest → dbt run/test')
    parser.add_argument('--excel', default='data/Data Engineer Challenge.xlsx', help='Ruta al Excel fuente')
    parser.add_argument('--duckdb', default='dbt/data_challenge.duckdb', help='Ruta a DuckDB')
    parser.add_argument('--raw_dir', default='raw_data', help='Directorio RAW local (Parquet)')
    parser.add_argument('--prod', action='store_true', help='Modo producción: sube RAW a S3')
    parser.add_argument('--s3_bucket', default=os.getenv('RAW_S3_BUCKET', ''), help='Bucket S3 RAW')
    parser.add_argument('--s3_prefix', default=os.getenv('RAW_S3_PREFIX', 'raw/loans'), help='Prefijo S3 RAW')
    parser.add_argument('--select', default='stg:* core:*', help='Selector dbt (run)')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]

    # 1) Ingesta a RAW (Parquet local + tabla raw.* en DuckDB)
    ingest_script = repo_root / 'ingest' / 'ingest_excel_to_duckdb.py'
    ingest_cmd = [
        'python', str(ingest_script),
        '--excel', str(repo_root / args.excel),
        '--duckdb', str(repo_root / args.duckdb),
        '--raw_dir', str(repo_root / args.raw_dir),
    ]
    if args.prod:
        if not args.s3_bucket:
            raise SystemExit('Error: --prod requiere --s3_bucket o env RAW_S3_BUCKET')
        ingest_cmd += ['--prod', '--s3_bucket', args.s3_bucket, '--s3_prefix', args.s3_prefix]
    run(ingest_cmd)

    # 2) dbt deps + run + test
    dbt_dir = repo_root / 'dbt'
    run(['dbt', 'deps'], cwd=str(dbt_dir))
    run(['dbt', 'run', '--select', args.select], cwd=str(dbt_dir))
    run(['dbt', 'test'], cwd=str(dbt_dir))

    print('✅ Pipeline completo')


if __name__ == '__main__':
    main()



