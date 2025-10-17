#!/bin/bash

# Function to detect database type from DATABASE_URL
detect_db_type() {
    if [[ "$DATABASE_URL" == *"mysql"* ]]; then
        echo "mysql"
    elif [[ "$DATABASE_URL" == *"postgresql"* ]]; then
        echo "postgres"
    else
        echo "postgres"  # Default to PostgreSQL
    fi
}

# Function to get the default port for a database type
get_db_port() {
    local db_type=$1
    case $db_type in
        "mysql")
            echo "3306"
            ;;
        "postgres")
            echo "5432"
            ;;
        *)
            echo "5432"  # Default to PostgreSQL port
            ;;
    esac
}

# Detect database type and get appropriate port
DB_TYPE=$(detect_db_type)
DB_PORT=$(get_db_port $DB_TYPE)

echo "Detected database type: $DB_TYPE (port: $DB_PORT)"

# Wait for the database to be ready
echo "Waiting for database to be ready..."
wait-for-db.sh db $DB_PORT

# Start the FastAPI server in the background
echo "Starting FastAPI server on port 8000..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit app
echo "Starting Streamlit app on port 8501..."
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Wait for all background processes to complete
wait
