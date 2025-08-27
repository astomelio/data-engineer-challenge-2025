#!/bin/bash

# Script to manage Airflow DAGs for the Data Engineer Challenge project
# This script helps you identify and manage only YOUR DAGs, not the example ones

echo "🔍 Data Engineer Challenge - DAG Management"
echo "=========================================="

# Function to show only project DAGs
show_my_dags() {
    echo "📋 Your Project DAGs:"
    echo "-------------------"
    airflow dags list | grep "loan_data_pipeline" || echo "No project DAGs found"
    echo ""
}

# Function to pause all example DAGs
pause_examples() {
    echo "⏸️  Pausing all example DAGs..."
    airflow dags list | grep "example_dags" | awk '{print $1}' | xargs -I {} airflow dags pause {} 2>/dev/null
    echo "✅ Example DAGs paused"
    echo ""
}

# Function to show DAG status
show_status() {
    echo "📊 DAG Status:"
    echo "-------------"
    airflow dags list | grep "loan_data_pipeline" | while read line; do
        dag_id=$(echo $line | awk '{print $1}')
        status=$(echo $line | awk '{print $4}')
        if [ "$status" = "False" ]; then
            echo "🟢 $dag_id - ACTIVE"
        else
            echo "🔴 $dag_id - PAUSED"
        fi
    done
    echo ""
}

# Function to run a specific DAG
run_dag() {
    local dag_id=$1
    if [ -z "$dag_id" ]; then
        echo "❌ Please specify a DAG ID"
        echo "Usage: $0 run <dag_id>"
        echo "Available DAGs:"
        airflow dags list | grep "loan_data_pipeline" | awk '{print "  - " $1}'
        return 1
    fi
    
    echo "🚀 Running DAG: $dag_id"
    airflow dags trigger $dag_id
    echo "✅ DAG triggered successfully"
    echo ""
}

# Function to show DAG details
show_dag_details() {
    local dag_id=$1
    if [ -z "$dag_id" ]; then
        echo "❌ Please specify a DAG ID"
        echo "Usage: $0 details <dag_id>"
        return 1
    fi
    
    echo "📋 DAG Details: $dag_id"
    echo "----------------------"
    airflow dags show $dag_id
    echo ""
}

# Main script logic
case "$1" in
    "list"|"")
        show_my_dags
        show_status
        ;;
    "pause-examples")
        pause_examples
        show_my_dags
        ;;
    "status")
        show_status
        ;;
    "run")
        run_dag "$2"
        ;;
    "details")
        show_dag_details "$2"
        ;;
    "help")
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  list              Show your project DAGs (default)"
        echo "  pause-examples    Pause all example DAGs"
        echo "  status            Show status of your DAGs"
        echo "  run <dag_id>      Trigger a specific DAG"
        echo "  details <dag_id>  Show detailed info about a DAG"
        echo "  help              Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                           # Show your DAGs"
        echo "  $0 run loan_data_pipeline    # Run the main pipeline"
        echo "  $0 details loan_data_pipeline_incremental  # Show incremental DAG details"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
