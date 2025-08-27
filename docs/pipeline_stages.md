# 📊 Etapas del Pipeline - Flujo Completo

## 📋 Descripción

Este documento describe en detalle cada etapa del pipeline de datos, desde la ingesta inicial hasta la generación de documentación, incluyendo el script de procesamiento Python.

## 🔄 Flujo Completo del Pipeline

### 1️⃣ **Etapa de Ingesta (RAW) - Script Python**
```
📥 Input: Data Engineer Challenge.xlsx
    ↓
🔧 Procesamiento: ingest_excel_to_duckdb.py
    ↓
📊 Outputs:
   ├── raw_data/raw_loans_<hash>.parquet
   ├── dbt/data_challenge.duckdb (raw.raw_loans) ← TABLA RAW CREADA AQUÍ
   └── s3://bucket/raw/loans/ (modo producción)
```

**⚠️ IMPORTANTE: La capa RAW se crea desde el script Python, NO desde dbt**

**Responsabilidades del Script Python:**
- ✅ Lectura del archivo Excel
- ✅ Validación de datos fuente
- ✅ Escritura en formato Parquet
- ✅ **Creación de la tabla `raw.raw_loans` en DuckDB**
- ✅ Upload opcional a S3

**☁️ PRODUCCIÓN vs DESARROLLO:**
- **Desarrollo (Actual)**: RAW almacenado en DuckDB local
- **Producción (AWS)**: RAW debería almacenarse en S3 buckets
- **Migración**: Script incluye funcionalidad S3 para producción

### 2️⃣ **Etapa de Transformación (SILVER) - dbt**
```
📥 Input: raw.raw_loans (creada por el script Python)
    ↓
🔧 Procesamiento: dbt run --select silver_loans
    ↓
📊 Output: silver.silver_loans
```

**Responsabilidades de dbt:**
- ✅ Limpieza de datos
- ✅ Deduplicación (18% de registros removidos)
- ✅ Normalización de formatos
- ✅ Validación de tipos de datos
- ✅ Estandarización de valores

### 3️⃣ **Etapa de Modelado (GOLD) - dbt**
```
📥 Input: silver.silver_loans
    ↓
🔧 Procesamiento: dbt run --select gold:*
    ↓
📊 Outputs:
   ├── gold.fact_loan
   ├── gold.dim_customer
   └── gold.dim_purpose
```

**Responsabilidades de dbt:**
- ✅ Creación de modelo dimensional
- ✅ Separación de hechos y dimensiones
- ✅ Optimización para analytics
- ✅ Generación de claves únicas

### 4️⃣ **Etapa de Validación - dbt**
```
📥 Input: Todas las tablas GOLD
    ↓
🔧 Procesamiento: dbt test
    ↓
📊 Output: Reporte de validación
```

**Responsabilidades:**
- ✅ Tests de integridad referencial
- ✅ Validación de rangos de valores
- ✅ Verificación de unicidad
- ✅ Checks de completitud

### 5️⃣ **Etapa de Documentación - dbt**
```
📥 Input: Modelos dbt
    ↓
🔧 Procesamiento: dbt docs generate
    ↓
📊 Output: Documentación HTML
```

**Responsabilidades:**
- ✅ Generación de documentación automática
- ✅ Lineage de datos
- ✅ Descripción de modelos
- ✅ Métricas de calidad

## 🔧 Script de Procesamiento Python - CREADOR DE RAW

### 📋 Descripción

El script `ingest_excel_to_duckdb.py` es el **creador de la capa RAW**, responsable de ingerir los datos del archivo Excel y cargarlos en la tabla `raw.raw_loans` en DuckDB.

### 🎯 Funcionalidades

#### 📊 Procesamiento de Datos
- ✅ **Lectura de Excel**: Pandas para procesar archivos .xlsx
- ✅ **Escritura Parquet**: Almacenamiento eficiente en formato columnar
- ✅ **Carga DuckDB**: Base de datos embebida para procesamiento
- ✅ **S3 Upload**: Opcional para entornos de producción

#### 🔄 Flujo de Procesamiento

```
Excel File → Pandas DataFrame → Parquet Files → DuckDB Table (raw.raw_loans)
     ↓              ↓              ↓              ↓
  Raw Data    →  Processing   →  Storage    →  Database
```

### 📁 Archivo Principal

#### `ingest/ingest_excel_to_duckdb.py`
```python
#!/usr/bin/env python3
"""
Script de ingesta: Excel → RAW (Parquet + DuckDB)
CREADOR DE LA CAPA RAW - Primer paso del pipeline de datos de préstamos.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import Optional

import duckdb
import pandas as pd
import boto3
from botocore.exceptions import ClientError

def read_excel_data(excel_path: Path) -> pd.DataFrame:
    """Lee el archivo Excel y retorna un DataFrame limpio"""
    try:
        print(f"📖 Leyendo Excel: {excel_path}")
        df = pd.read_excel(excel_path)
        print(f"✅ Excel leído: {len(df)} filas, {len(df.columns)} columnas")
        return df
    except Exception as e:
        raise FileNotFoundError(f"Error leyendo Excel: {e}")

def write_parquet(df: pd.DataFrame, raw_dir: Path) -> Path:
    """Escribe el DataFrame como archivo Parquet"""
    try:
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre único basado en contenido
        content_hash = hashlib.md5(df.to_string().encode()).hexdigest()
        parquet_path = raw_dir / f"raw_loans_{content_hash}.parquet"
        
        df.to_parquet(parquet_path, index=False)
        print(f"✅ RAW Parquet escrito: {parquet_path}")
        return parquet_path
    except Exception as e:
        raise RuntimeError(f"Error escribiendo Parquet: {e}")

def load_to_duckdb(df: pd.DataFrame, duckdb_path: Path) -> None:
    """Carga el DataFrame a DuckDB - CREA LA TABLA RAW"""
    try:
        # Crear directorio si no existe
        duckdb_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Conectar a DuckDB
        con = duckdb.connect(str(duckdb_path))
        
        # Crear esquema raw si no existe
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        
        # Cargar datos - ESTO CREA LA TABLA raw.raw_loans
        con.execute("DROP TABLE IF EXISTS raw.raw_loans")
        con.execute("CREATE TABLE raw.raw_loans AS SELECT * FROM df")
        
        # Verificar carga
        count = con.execute("SELECT COUNT(*) FROM raw.raw_loans").fetchone()[0]
        print(f"✅ Ingestado en DuckDB → tabla raw.raw_loans en {duckdb_path}")
        print(f"   Registros cargados: {count}")
        
        con.close()
    except Exception as e:
        raise RuntimeError(f"Error cargando a DuckDB: {e}")

def upload_to_s3(parquet_path: Path, bucket: str, prefix: str) -> None:
    """Sube el archivo Parquet a S3 (modo producción)"""
    try:
        s3_client = boto3.client('s3')
        
        # Generar clave S3
        s3_key = f"{prefix}/{parquet_path.name}"
        
        # Subir archivo
        s3_client.upload_file(str(parquet_path), bucket, s3_key)
        print(f"✅ Subido a S3: s3://{bucket}/{s3_key}")
    except ClientError as e:
        raise RuntimeError(f"Error subiendo a S3: {e}")

def main():
    """Función principal del script de ingesta - CREADOR DE RAW"""
    parser = argparse.ArgumentParser(description='Ingesta Excel → RAW (Parquet + DuckDB)')
    parser.add_argument('--excel', required=True, type=Path, help='Ruta al archivo Excel')
    parser.add_argument('--duckdb', required=True, type=Path, help='Ruta a DuckDB')
    parser.add_argument('--raw_dir', required=True, type=Path, help='Directorio RAW (Parquet)')
    parser.add_argument('--prod', action='store_true', help='Modo producción (S3)')
    parser.add_argument('--s3_bucket', help='Bucket S3')
    parser.add_argument('--s3_prefix', default='raw/loans', help='Prefijo S3')
    
    args = parser.parse_args()
    
    # Validar archivo Excel
    if not args.excel.exists():
        raise FileNotFoundError(f"No existe el Excel: {args.excel}")
    
    print("🚀 Iniciando ingesta Excel → RAW")
    print("=" * 50)
    
    # 1. Leer Excel
    df = read_excel_data(args.excel)
    
    # 2. Escribir Parquet
    parquet_path = write_parquet(df, args.raw_dir)
    
    # 3. Cargar DuckDB - CREA LA TABLA raw.raw_loans
    load_to_duckdb(df, args.duckdb)
    
    # 4. Subir S3 (si modo producción)
    if args.prod:
        if not args.s3_bucket:
            raise ValueError("--prod requiere --s3_bucket")
        upload_to_s3(parquet_path, args.s3_bucket, args.s3_prefix)
    
    print("=" * 50)
    print("✅ Ingesta completada exitosamente")
    print("📊 Tabla raw.raw_loans creada y lista para dbt")

if __name__ == '__main__':
    main()
```

### 🔧 Configuración y Uso

#### 📋 Argumentos del Script
```bash
python ingest_excel_to_duckdb.py \
    --excel "Data Engineer Challenge.xlsx" \
    --duckdb "dbt/data_challenge.duckdb" \
    --raw_dir "raw_data"
```

#### 🚀 Modo Producción (S3)
```bash
python ingest_excel_to_duckdb.py \
    --excel "Data Engineer Challenge.xlsx" \
    --duckdb "dbt/data_challenge.duckdb" \
    --raw_dir "raw_data" \
    --prod \
    --s3_bucket "my-raw-data-bucket" \
    --s3_prefix "raw/loans"
```

#### 📊 Salidas del Script
- **Parquet Files**: `raw_data/raw_loans_<hash>.parquet`
- **DuckDB Table**: `raw.raw_loans` ← **TABLA RAW CREADA AQUÍ**
- **S3 Files**: `s3://bucket/prefix/raw_loans_<hash>.parquet` (modo producción)

## 📈 Métricas del Pipeline

### ⏱️ Tiempos de Ejecución
- **Ingesta (Python)**: ~30 segundos
- **Transformación SILVER (dbt)**: ~0.2 segundos
- **Transformación GOLD (dbt)**: ~0.4 segundos
- **Tests**: ~0.1 segundos
- **Total**: ~1 minuto

### 📊 Volúmenes de Datos
- **Entrada**: 100,000 registros
- **SILVER**: 81,999 registros (18% deduplicación)
- **GOLD**: 81,999 registros + dimensiones

### 🎯 Calidad de Datos
- **Tests pasados**: 5/5 (100%)
- **Deduplicación**: 18,001 registros removidos
- **Validación**: Todos los rangos correctos

## 🔄 Orquestación con Airflow

### 📊 Estructura del DAG
```
loan_data_pipeline
├── ingest_excel_to_raw     # Etapa 1: Ingestión (CREA RAW)
├── dbt_deps                # Etapa 2: Dependencias
├── dbt_run_models          # Etapa 3: Transformaciones (SILVER + GOLD)
├── dbt_run_tests           # Etapa 4: Validación
├── validate_data_quality   # Etapa 5: Checks adicionales
└── dbt_generate_docs       # Etapa 6: Documentación
```

### ⏰ Programación
- **Frecuencia**: Diaria
- **Hora**: Configurable
- **Retry**: Automático en fallos
- **Timeout**: Configurable por tarea

## 🚀 Optimizaciones Implementadas

### 📊 **Performance**
- **Parquet**: Formato columnar eficiente
- **DuckDB**: Base de datos embebida rápida
- **Deduplicación**: Eliminación temprana de duplicados
- **Índices**: Automáticos en DuckDB

### 🔍 **Calidad**
- **Validación**: Tests automáticos en cada etapa
- **Logging**: Logs detallados para debugging
- **Checks**: Validación de conteos y rangos
- **Documentación**: Generación automática

### 🛡️ **Robustez**
- **Error Handling**: Manejo de errores en cada función
- **Retry Logic**: Reintentos automáticos en Airflow
- **Validation**: Verificación de datos en cada paso
- **Monitoring**: Monitoreo en tiempo real

## 🔧 Comandos de Ejecución

### 📊 Pipeline Completo
```bash
# Opción 1: Script local
python scripts/run_pipeline.py

# Opción 2: Airflow
airflow dags trigger loan_data_pipeline

# Opción 3: Etapas individuales
python ingest/ingest_excel_to_duckdb.py --excel "Data Engineer Challenge.xlsx" --duckdb "dbt/data_challenge.duckdb" --raw_dir "raw_data"
cd dbt && dbt run
cd dbt && dbt test
```

### 🔍 Monitoreo
```bash
# Logs de Airflow
tail -f airflow/logs/dag_id/task_id/run_id/task_id.log

# Logs de dbt
cd dbt && dbt run --log-level debug

# Explorar base de datos
python scripts/explore_db.py
```

## 🎯 Resultados Finales

### 📊 **Base de Datos Final**
- **Esquemas**: `raw`, `silver`, `gold`
- **Tablas**: 5 tablas principales
- **Registros**: 81,999 registros limpios
- **Dimensiones**: 2 tablas de dimensiones

### 📈 **Métricas de Calidad**
- **Deduplicación**: 18% de registros removidos
- **Tests**: 100% de tests pasando
- **Validación**: Todos los rangos correctos
- **Documentación**: Completa y actualizada

### 🚀 **Performance**
- **Tiempo total**: ~1 minuto
- **Escalabilidad**: Preparado para volúmenes mayores
- **Monitoreo**: En tiempo real
- **Mantenimiento**: Automatizado

## ⚠️ **Puntos Clave a Recordar**

### 🔴 **RAW se crea desde Python, NO desde dbt**
- El script `ingest_excel_to_duckdb.py` crea la tabla `raw.raw_loans`
- dbt solo lee desde `raw.raw_loans` para crear SILVER y GOLD
- No hay modelos dbt en la carpeta `raw/` porque no los necesitamos
- **☁️ PRODUCCIÓN**: En AWS, el script debería subir datos a S3 en lugar de DuckDB local

### 🟡 **SILVER y GOLD se crean desde dbt**
- `silver/silver_loans.sql` transforma `raw.raw_loans`
- `gold/*.sql` transforma `silver.silver_loans`

### 🟢 **Flujo de Dependencias**
```
Python Script → raw.raw_loans → dbt silver → dbt gold
```

---

*Documentación de Etapas del Pipeline - Pipeline de Préstamos v1.0*
