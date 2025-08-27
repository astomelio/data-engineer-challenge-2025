#!/bin/bash

# Script súper simple para ver solo TUS DAGs
echo "🔍 TUS DAGs del proyecto:"
echo "========================"

# Mostrar solo tus DAGs
airflow dags list | grep "loan_data_pipeline"

echo ""
echo "💡 Para ejecutar un DAG:"
echo "   airflow dags trigger loan_data_pipeline"
echo "   airflow dags trigger loan_data_pipeline_incremental"
