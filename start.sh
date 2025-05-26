#!/bin/bash

# Load environment variables
source .env

# Create upload directory if it doesn't exist
mkdir -p /home/llm/flask-whisperx-api/tmp/whisperx_uploads

# Start the application with Gunicorn
exec gunicorn --config gunicorn_config.py wsgi:app
