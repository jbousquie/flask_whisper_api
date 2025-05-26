#!/bin/bash

# Script to run the WhisperX API in development mode
# This script suppresses the SpeechBrain deprecation warning

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

# Create upload directory if it doesn't exist
UPLOAD_DIR=${UPLOAD_FOLDER:-"/tmp/whisperx_uploads"}
mkdir -p "$UPLOAD_DIR"
echo "Upload directory created at: $UPLOAD_DIR"

# Set environment variable to ignore the warning
export PYTHONWARNINGS="ignore:Module 'speechbrain.pretrained' was deprecated"

# Start the Flask development server
echo "Starting WhisperX API development server..."
python app.py