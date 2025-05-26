#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import requests
import sys

# Load environment variables
load_dotenv()

def check_model_access(model_id, token):
    """Check if the token has access to the model."""
    url = f"https://huggingface.co/api/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    return False

def main():
    # Get token from environment
    token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    
    if not token:
        print("Error: No Hugging Face token found in .env file.")
        print("Please add your token to the .env file as HF_TOKEN=your_token_here")
        sys.exit(1)
    
    # Models to check
    models = [
        "pyannote/segmentation",
        "pyannote/speaker-diarization",
        "pyannote/speaker-diarization-3.1"
    ]
    
    print(f"Checking access to required models with token: {token[:5]}...{token[-5:]}")
    
    all_access = True
    for model in models:
        access = check_model_access(model, token)
        status = "✓ Access granted" if access else "✗ Access denied"
        print(f"{status} for {model}")
        
        if not access:
            all_access = False
            print(f"  Please visit https://huggingface.co/{model} to accept the user conditions.")
    
    if all_access:
        print("\nSuccess! Your token has access to all required models.")
    else:
        print("\nPlease make sure you have accepted the user conditions for all models.")
        print("After accepting, try running this script again.")
        print("\nVisit https://huggingface.co/settings/tokens to manage your tokens.")

if __name__ == "__main__":
    main()
