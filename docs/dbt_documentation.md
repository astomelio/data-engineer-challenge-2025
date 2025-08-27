# 🎯 Documentación dbt - Transformaciones de Datos

## 📋 Descripción

**dbt (data build tool)** se utiliza para transformar los datos desde la capa RAW hasta las capas SILVER y GOLD, implementando un modelo dimensional optimizado para analytics.

## 🏗️ Arquitectura dbt

### 📊 Capas de Transformación

#### 🔴 RAW Layer (Fuente) - CREADA POR PYTHON
- **Tabla**: `raw.raw_loans`
- **Contenido**: Datos originales del Excel sin procesar
- **Registros**: 100,000
- **Propósito**: Preservar datos originales
- **⚠️ IMPORTANTE**: Esta tabla se crea desde el script `ingest_excel_to_duckdb.py`, NO desde dbt
- **🎯 MEJOR PRÁCTICA**: Definida como **source** en dbt para mejor trazabilidad
- **☁️ PRODUCCIÓN**: En AWS, esta capa debería almacenarse en S3, no en DuckDB local

#### 🟡 SILVER Layer (Staging) - CREADA POR DBT
- **Tabla**: `silver.silver_loans`
- **Contenido**: Datos limpios y deduplicados
- **Registros**: 81,999 (18% de duplicados removidos)
- **Propósito**: Limpieza y validación
- **Fuente**: Lee desde `{{ source('raw', 'raw_loans') }}`

#### 🟢 GOLD Layer (Analytics) - CREADA POR DBT
- **Fact Table**: `gold.fact_loan`
- **Dimension Tables**: 
  - `gold.dim_customer`
  - `gold.dim_purpose`
- **Propósito**: Modelo dimensional para analytics
- **Fuente**: Lee desde `{{ ref('silver_loans') }}`

## 📁 Archivos dbt

### 🔧 Configuración

#### `dbt_project.yml`
```yaml
name: 'data_challenge'
version: '1.0.0'
config-version: 2

# Configuración de esquemas
models:
  data_challenge:
    silver:
      +materialized: table
      +schema: silver
    gold:
      +materialized: table
      +schema: gold
```

#### `packages.yml`
```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: "=1.3.0"  # Versión compatible con dbt-core 1.10
```

### 🎯 Modelos

#### `models/silver/silver_loans.sql` - Capa SILVER
```sql
{# DuckDB local - Silver Layer #}
with src as (
    select * from {{ source('raw', 'raw_loans') }}
),
clean as (
    select
        "Loan ID"::varchar                        as loan_id,
        "Customer ID"::varchar                    as customer_id,
        nullif("Current Loan Amount", 99999999)   as current_loan_amount,
        case
            when "Credit Score" is null then null
            when "Credit Score" > 900 then round("Credit Score"/10.0)
            else round("Credit Score")
        end::int                                   as credit_score,
        case when lower(coalesce("Term", '')) like '%short%' then 'Short Term' else 'Long Term' end as term,
        replace(coalesce(nullif(trim("Purpose"), ''), 'Other'), '_', ' ') as purpose_name,
        case
            when "Home Ownership" in ('Home Mortgage','HaveMortgage') then 'Mortgage'
            when "Home Ownership" = 'Own Home' then 'Own'
            when "Home Ownership" = 'Rent' then 'Rent'
            else 'Other'
        end                                         as home_ownership,
        try_cast(regexp_extract(coalesce("Years in current job", ''), '([0-9]+)', 1) as int) as job_tenure_years,
        "Loan Status"                               as loan_status,
        "Annual Income"                             as annual_income,
        "Monthly Debt"                              as monthly_debt,
        "Years of Credit History"                   as years_credit_history,
        "Months since last delinquent"              as months_since_last_delinquent,
        "Number of Open Accounts"                   as n_open_accounts,
        "Number of Credit Problems"                 as n_credit_problems,
        "Current Credit Balance"                    as current_credit_balance,
        "Maximum Open Credit"                       as max_open_credit,
        coalesce("Bankruptcies",0)                  as bankruptcies,
        coalesce("Tax Liens",0)                     as tax_liens
    from src
),
ranked as (
    select
        *,
        row_number() over (partition by loan_id order by loan_id) as rn
    from clean
)
select
    loan_id,
    customer_id,
    current_loan_amount,
    credit_score,
    term,
    purpose_name,
    home_ownership,
    job_tenure_years,
    loan_status,
    annual_income,
    monthly_debt,
    years_credit_history,
    months_since_last_delinquent,
    n_open_accounts,
    n_credit_problems,
    current_credit_balance,
    max_open_credit,
    bankruptcies,
    tax_liens
from ranked
where rn = 1
```

**Características principales:**
- ✅ **Source Reference**: Usa `{{ source('raw', 'raw_loans') }}` para mejor trazabilidad
- ✅ **Deduplicación**: `row_number()` para eliminar duplicados
- ✅ **Limpieza**: Normalización de valores nulos y formatos
- ✅ **Validación**: Conversión segura de tipos de datos
- ✅ **Estandarización**: Formato consistente para propósito

#### `models/gold/dim_customer.sql` - Dimensión Cliente
```sql
select distinct
  customer_id,
  job_tenure_years,
  home_ownership
from {{ ref('silver_loans') }}
```

**Propósito**: Tabla de dimensiones para atributos del cliente

#### `models/gold/dim_purpose.sql` - Dimensión Propósito
```sql
with silver as (
  select distinct purpose_name from {{ ref('silver_loans') }}
)
select
  purpose_name,
  dense_rank() over(order by purpose_name) as purpose_id
from silver
```

**Propósito**: Tabla de dimensiones para propósitos de préstamo

#### `models/gold/fact_loan.sql` - Tabla de Hechos
```sql
with s as (
  select * from {{ ref('silver_loans') }}
), p as (
  select * from {{ ref('dim_purpose') }}
)
select
  s.loan_id,
  s.customer_id,
  p.purpose_id,
  s.loan_status,
  s.term,
  s.credit_score,
  s.current_loan_amount,
  s.annual_income,
  s.monthly_debt,
  s.years_credit_history,
  s.months_since_last_delinquent,
  s.n_open_accounts,
  s.n_credit_problems,
  s.current_credit_balance,
  s.max_open_credit,
  s.bankruptcies,
  s.tax_liens
from s
left join p using (purpose_name)
```

**Propósito**: Tabla de hechos con métricas de préstamos

### 🧪 Tests y Validación

#### `models/sources.yml` - Definición de Sources
```yaml
version: 2
sources:
  - name: raw
    description: "Raw data layer - datos originales del Excel cargados por el script Python"
    schema: raw
    tables:
      - name: raw_loans
        description: "Datos originales de préstamos desde el archivo Excel"
        columns:
          - name: "Loan ID"
            description: "Identificador único del préstamo"
            tests:
              - not_null
          - name: "Customer ID"
            description: "Identificador único del cliente"
            tests:
              - not_null
          # ... más columnas definidas
```

#### `models/schema.yml` - Tests de Modelos
```yaml
version: 2

models:
  - name: silver_loans
    description: "Staging table for loan data"
    columns:
      - name: loan_id
        description: "Unique loan identifier"
        tests:
          - not_null
          - unique
      - name: loan_status
        description: "Status of the loan"
        tests:
          - accepted_values:
              values: ['Fully Paid', 'Charged Off']
      - name: credit_score
        description: "Credit score of the borrower"
        tests:
          - dbt_utils.accepted_range:
              min_value: 300
              max_value: 850

  - name: fact_loan
    description: "Fact table for loan metrics"
    columns:
      - name: loan_id
        description: "Unique loan identifier"
        tests:
          - dbt_utils.unique_combination_of_columns:
              combination_of_columns:
                - loan_id
```

### 📊 Resultados del Pipeline

#### Estadísticas de Datos
- **RAW**: 100,000 registros originales (creados por Python)
- **SILVER**: 81,999 registros (18% de duplicados removidos) (creados por dbt)
- **GOLD**: 
  - Fact Table: 81,999 registros (creados por dbt)
  - Dim Customer: 81,999 clientes únicos (creados por dbt)
  - Dim Purpose: 16 propósitos únicos (creados por dbt)

#### Distribución de Estados
- **Fully Paid**: 59,360 (72.4%)
- **Charged Off**: 22,639 (27.6%)

#### Propósitos Principales
- **Debt Consolidation**: 64,907 (79.2%)
- **Home Improvements**: 4,795 (5.8%)
- **Other**: 7,238 (8.8%)

## 🔧 Comandos dbt

### 📊 Ejecución de Modelos
```bash
# Ejecutar todos los modelos
dbt run

# Ejecutar solo silver
dbt run --select silver:*

# Ejecutar solo gold
dbt run --select gold:*

# Ejecutar modelo específico
dbt run --select silver_loans
```

### 🧪 Ejecución de Tests
```bash
# Ejecutar todos los tests
dbt test

# Ejecutar tests de sources
dbt test --select source:raw

# Ejecutar tests de un modelo específico
dbt test --select silver_loans

# Ejecutar test específico
dbt test --select silver_loans:unique
```

### 📚 Documentación
```bash
# Generar documentación
dbt docs generate

# Servir documentación
dbt docs serve
```

### 🔄 Dependencias
```bash
# Instalar dependencias
dbt deps

# Limpiar cache
dbt clean
```

## 🎯 Mejores Prácticas Implementadas

### ✅ **Uso de Sources**
- **Ventaja**: Mejor trazabilidad y documentación
- **Beneficio**: dbt puede detectar cambios en las sources
- **Práctica**: `{{ source('raw', 'raw_loans') }}` en lugar de referencias directas

### ✅ **Deduplicación**
- Uso de `row_number()` para eliminar duplicados en SILVER
- Preservación de datos originales en RAW

### ✅ **Limpieza de Datos**
- Normalización de valores nulos con `coalesce()`
- Conversión segura de tipos con `try_cast()`
- Estandarización de formatos

### ✅ **Validación**
- Tests de unicidad para identificadores
- Validación de rangos para valores numéricos
- Tests de valores aceptados para categorías

### ✅ **Modelado Dimensional**
- Separación clara entre hechos y dimensiones
- Claves únicas para dimensiones
- Optimización para queries analíticas

## 🚀 Optimizaciones

### 📊 **Performance**
- Materialización como tablas para queries rápidas
- Índices automáticos en DuckDB
- Particionamiento por esquemas

### 🔍 **Debugging**
- Logs detallados con `--log-level debug`
- Documentación automática de lineage
- Tests para validación continua

## ⚠️ **Puntos Clave a Recordar**

### 🔴 **RAW se crea desde Python, NO desde dbt**
- El script `ingest_excel_to_duckdb.py` crea la tabla `raw.raw_loans`
- dbt solo lee desde `raw.raw_loans` para crear SILVER y GOLD
- No hay modelos dbt en la carpeta `raw/` porque no los necesitamos
- **☁️ PRODUCCIÓN**: En AWS, el script debería subir datos a S3 en lugar de DuckDB local

### 🟡 **SILVER y GOLD se crean desde dbt**
- `silver/silver_loans.sql` transforma `{{ source('raw', 'raw_loans') }}`
- `gold/*.sql` transforma `{{ ref('silver_loans') }}`

### 🟢 **Flujo de Dependencias**
```
Python Script → raw.raw_loans → dbt silver → dbt gold
```

### 🎯 **Ventajas de usar Sources**
- ✅ **Trazabilidad**: dbt puede detectar cambios en las sources
- ✅ **Documentación**: Mejor documentación automática
- ✅ **Tests**: Tests específicos para sources
- ✅ **Lineage**: Mejor visualización del lineage en dbt docs

---

*Documentación dbt - Pipeline de Préstamos v1.0*
