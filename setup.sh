#!/bin/bash

echo "Setting up WhisperX Flask API..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your Hugging Face token."
else
    echo ".env file already exists."
fi

# Make start script executable
echo "Making start script executable..."
chmod +x start.sh

echo "Setup complete! To activate the virtual environment, run: source venv/bin/activate"
