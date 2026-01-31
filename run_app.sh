#!/bin/bash
# ========================================
# Streamlit Application Launcher
# ========================================
# This script activates the virtual environment
# and launches the Streamlit application

# Activate the Python virtual environment
source .venv/bin/activate

# Run the Streamlit app with the main application file
streamlit run src/app.py
