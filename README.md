# 🚀 Data Engineer Challenge - Pipeline de Préstamos

## 📋 Descripción General

Este proyecto implementa un **pipeline de datos completo** para procesar información de préstamos desde un archivo Excel hasta un modelo dimensional optimizado para analytics. El pipeline sigue la arquitectura **RAW → SILVER → GOLD** y utiliza **Apache Airflow** para orquestación.

## 🏗️ Arquitectura del Pipeline

### 📊 Capas de Datos

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LANDING       │    │     SILVER      │    │      GOLD       │
│   (RAW)         │───▶│   (Structured)  │───▶│   (Analytics)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│ • Excel Source  │    │ • Cleaned Data  │    │ • Fact Tables   │
│ • Parquet Files │    │ • Deduplication │    │ • Dimension     │
│ • Raw Tables    │    │ • Validation    │    │ • Star Schema   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 Flujo de Datos

1. **LANDING (RAW)**: Datos originales del Excel → `raw.raw_loans` en DuckDB
2. **SILVER**: Datos limpios y estructurados → `silver.silver_loans`
3. **GOLD**: Modelo dimensional para analytics → `gold.fact_loan`, `gold.dim_*`

### ⚠️ **Arquitectura Actual vs Producción**
- **Desarrollo (Actual)**: RAW almacenado en DuckDB local
- **Producción (AWS)**: RAW debería almacenarse en S3 buckets
- **Migración**: Script incluye funcionalidad S3 para producción

## 📁 Estructura del Proyecto

```
data_engineer_challenge_local_duckdb/
├── 📊 data/                          # Datos fuente
│   └── Data Engineer Challenge.xlsx  # Archivo Excel original
├── 🔧 ingest/                        # Scripts de ingesta
│   └── ingest_excel_to_duckdb.py    # Procesamiento inicial
├── 🎯 dbt/                          # Transformaciones dbt
│   ├── models/
│   │   ├── silver/                  # Capa SILVER
│   │   │   └── silver_loans.sql     # Limpieza y deduplicación
│   │   └── gold/                    # Capa GOLD
│   │       ├── dim_customer.sql     # Dimensión clientes
│   │       ├── dim_purpose.sql      # Dimensión propósitos
│   │       └── fact_loan.sql        # Tabla de hechos
│   ├── dbt_project.yml
│   └── packages.yml
├── ☁️ airflow/                      # Orquestación Airflow
│   ├── dags/
│   │   └── loan_pipeline_dag.py
│   └── utils/
│       ├── pipeline_functions.py
│       └── config.py
├── 📜 scripts/                      # Scripts de utilidad
│   ├── run_pipeline.py
│   └── explore_db.py
├── 📚 docs/                         # Documentación técnica
│   ├── dbt_documentation.md
│   ├── airflow_documentation.md
│   └── pipeline_stages.md
└── 📚 README.md                     # Esta documentación
```

## 🚀 Inicio Rápido

### 📋 Prerrequisitos
- Python 3.13+
- Apache Airflow 3.0.4+
- dbt-core 1.10.9+
- DuckDB

### 🔧 Instalación

1. **Clonar y configurar**
```bash
git clone <repository-url>
cd data_engineer_challenge_local_duckdb
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar Airflow**
```bash
export AIRFLOW_HOME=$(pwd)/airflow
export PYTHONPATH=$PYTHONPATH:$(pwd)/airflow
airflow standalone
```

### 🎯 Ejecución

#### Opción 1: Pipeline Local
```bash
python scripts/run_pipeline.py
```

#### Opción 2: Pipeline con Airflow
1. Acceder a http://localhost:8080 (admin/cvPPAEfuV7bSTP6s)
2. Buscar DAG `loan_data_pipeline`
3. Hacer clic en "Trigger DAG"

#### Opción 3: Explorar Base de Datos
```bash
python scripts/explore_db.py
```

## 📊 Resultados del Pipeline

### 📈 Estadísticas de Datos
- **RAW**: 100,000 registros originales (`raw.raw_loans`)
- **SILVER**: 81,999 registros (18% de duplicados removidos) (`silver.silver_loans`)
- **GOLD**: 
  - Fact Table: 81,999 registros (`gold.fact_loan`)
  - Dim Customer: 81,999 clientes únicos (`gold.dim_customer`)
  - Dim Purpose: 16 propósitos únicos (`gold.dim_purpose`)

### 🎯 Distribución de Estados
- **Fully Paid**: 59,360 (72.4%)
- **Charged Off**: 22,639 (27.6%)

### 📋 Propósitos Principales
- **Debt Consolidation**: 64,907 (79.2%)
- **Home Improvements**: 4,795 (5.8%)
- **Other**: 7,238 (8.8%)

## 📚 Documentación Técnica

Para información detallada sobre cada componente:

- **[Documentación dbt](docs/dbt_documentation.md)** - Transformaciones y modelos
- **[Documentación Airflow](docs/airflow_documentation.md)** - Orquestación y configuración
- **[Etapas del Pipeline](docs/pipeline_stages.md)** - Flujo completo y métricas

## 🔧 Comandos Útiles

### 📊 Monitoreo
```bash
# Ver logs de Airflow
tail -f airflow/logs/dag_id/task_id/run_id/task_id.log

# Ejecutar dbt con debug
cd dbt && dbt run --log-level debug
```

### 🧹 Mantenimiento
```bash
# Limpiar dbt
cd dbt && dbt clean

# Reprocesar desde cero
python scripts/run_pipeline.py
```

## 🎯 Características Principales

- ✅ **Escalabilidad**: Preparado para S3 en producción (RAW layer)
- ✅ **Calidad**: Tests automáticos y validación
- ✅ **Documentación**: Generación automática de docs
- ✅ **Monitoreo**: Airflow para orquestación
- ✅ **Flexibilidad**: Múltiples opciones de ejecución

## 🚀 Próximos Pasos

- Implementar alertas de calidad
- Agregar más tests de negocio
- Optimizar para volúmenes mayores
- Implementar versionado de datos

---

*Pipeline de Préstamos v1.0 - Documentación simplificada*

