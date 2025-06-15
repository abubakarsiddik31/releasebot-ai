#!/bin/bash

# Wait for the database to be ready
wait-for-db.sh db 3306

# Start the FastAPI server in the background
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit app
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Wait for all background processes to complete
wait
