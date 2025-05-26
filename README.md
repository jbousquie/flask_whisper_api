# WhisperX Flask API

A Flask-based REST API for WhisperX with speaker diarization support.

## Features

- Audio transcription using WhisperX large-v2 model
- Speaker diarization with pyannote.audio
- GPU acceleration with CUDA support
- Multiple audio format support
- Production-ready with Gunicorn
- Health monitoring endpoints

## Setup

### 1. Create and activate a Python virtual environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your Hugging Face token
```

### 4. Accept the Hugging Face model terms

**Important**: Before running the application, you need to accept the user agreements for the pyannote models on Hugging Face:

1. Make sure you're logged into Hugging Face with the account associated with your token
2. Visit and accept the terms for the following models:
   - https://huggingface.co/pyannote/segmentation
   - https://huggingface.co/pyannote/speaker-diarization
   - https://huggingface.co/pyannote/speaker-diarization-3.1

### 5. Make start script executable

```bash
chmod +x start.sh
```

## Running the API

### Development
```bash
python app.py
```

### Production
```bash
./start.sh
```

## API Endpoints

### Health Check
```
GET /health
```

### Transcribe Audio
```
POST /transcribe
```

**Parameters:**
- `audio` (file): Audio file to transcribe
- `diarization` (bool, optional): Enable speaker diarization (default: false)
- `language` (string, optional): Language code (default: "en")
- `min_speakers` (int, optional): Minimum number of speakers (default: 1)
- `max_speakers` (int, optional): Maximum number of speakers (default: 10)

### Models Information
```
GET /models/info
```

## Supported Audio Formats

- WAV, MP3, MP4, AVI, MOV, MKV, FLAC, M4A, OGG

## Troubleshooting

### Diarization Model Issues

If you encounter errors related to loading the diarization models, verify:

1. Your Hugging Face token is valid and has been added to the .env file
2. You've accepted the user agreements for all required models on Hugging Face
3. Your account has appropriate access to the pyannote models
