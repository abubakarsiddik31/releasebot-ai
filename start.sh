#!/bin/bash

uvicorn src.main:app --host 0.0.0.0 --port 8000 &
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

wait 
