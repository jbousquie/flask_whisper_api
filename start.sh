#!/bin/bash

# Load environment variables
source .env

# Check for Python virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Python virtual environment not found."
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check Hugging Face model access before starting
echo "Checking Hugging Face model access..."
python check_hf_access.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to verify Hugging Face model access."
    echo "Please make sure you've accepted the model terms at huggingface.co."
    echo "For more information, see the README.md."
    exit 1
fi

# Create upload directory if it doesn't exist
UPLOAD_DIR=${UPLOAD_FOLDER:-"/tmp/whisperx_uploads"}
mkdir -p "$UPLOAD_DIR"
echo "Upload directory created at: $UPLOAD_DIR"

# Start the application with Gunicorn
echo "Starting WhisperX API server..."
exec gunicorn --config gunicorn_config.py wsgi:app
