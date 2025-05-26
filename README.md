# WhisperX Flask API

A Flask-based REST API for WhisperX with speaker diarization support, optimized for GPU usage.

## Features

- Audio transcription using WhisperX large-v3 model
- Speaker diarization with pyannote.audio
- GPU acceleration with CUDA 12.8 support
- Optimized for NVIDIA GPUs with 20GB VRAM
- Multiple audio format support
- Production-ready with Gunicorn
- Health monitoring endpoints
- Real-time system and GPU monitoring

## Setup Guide

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

Note: The API is configured to work with PyTorch 2.7.0 and CUDA 12.8.

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

### 5. Make scripts executable

```bash
chmod +x start.sh
chmod +x run_dev.sh
chmod +x monitor.py
```

### 6. Verify Hugging Face access

```bash
python check_hf_access.py
```

If this passes successfully, your Hugging Face token has the correct permissions to download and use all required models.

### 7. Test the API setup

```bash
# Test the API without processing audio
python test_client.py
```

This should check if the API can be reached and if all models are loaded correctly.

## Running the API

### Development Mode
```bash
# Make the script executable first
chmod +x run_dev.sh

# Run the development server (suppresses SpeechBrain warnings)
./run_dev.sh
```

Alternatively, you can run the Flask development server directly:
```bash
python app.py
```

### Production Mode
```bash
# Make the script executable first
chmod +x start.sh

# Run with Gunicorn for production use
./start.sh
```

### Monitoring the API
```bash
# Make the script executable first
chmod +x monitor.py

# Basic monitoring
./monitor.py

# Continuous monitoring with 10-second refresh interval
./monitor.py --continuous --interval 10

# Get JSON output for programmatic use
./monitor.py --json
```

### Testing the API
```bash
# Test basic API endpoints
python test_client.py

# Test transcription with an audio file
python test_client.py --audio /path/to/your/audio.wav

# Advanced options
python test_client.py --audio /path/to/your/audio.wav --language ja --no-diarization --min-speakers 2 --max-speakers 10
```

## API Endpoints

### Health Check
```
GET /health
```

Returns information about the API status, including GPU device detection and memory.

**Response example:**
```json
{
  "status": "healthy",
  "whisperx_loaded": true,
  "align_loaded": true,
  "diarize_loaded": true,
  "device": "cuda",
  "gpu_memory": 20.0
}
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

**Example cURL request:**
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio=@/path/to/audio.mp3" \
  -F "diarization=true" \
  -F "language=en" \
  -F "min_speakers=1" \
  -F "max_speakers=5"
```

### Models Information
```
GET /models/info
```

**Response example:**
```json
{
  "whisperx_model": "large-v3",
  "align_model_loaded": true,
  "diarization_available": true,
  "supported_formats": ["wav", "mp3", "mp4", "avi", "mov", "mkv", "flac", "m4a", "ogg"],
  "max_file_size_mb": 500
}
```

## Supported Audio Formats

- WAV, MP3, MP4, AVI, MOV, MKV, FLAC, M4A, OGG

## API Scripts

| Script | Description |
|--------|-------------|
| `app.py` | Main Flask application |
| `wsgi.py` | WSGI entry point for Gunicorn |
| `run_dev.sh` | Run in development mode with warning suppression |
| `start.sh` | Run in production mode with Gunicorn |
| `test_client.py` | Test the API endpoints |
| `monitor.py` | Monitor API and system health |
| `check_hf_access.py` | Verify Hugging Face token access |
| `gunicorn_config.py` | Gunicorn server configuration |

## System Requirements

- Python 3.8+
- NVIDIA GPU with CUDA 12.8 support
- 20GB+ VRAM recommended for large-v3 model
- PyTorch 2.7.0
- Sufficient disk space for model storage

## Troubleshooting

### Diarization Model Issues

If you encounter errors related to loading the diarization models, verify:

1. Your Hugging Face token is valid and has been added to the .env file
2. You've accepted the user agreements for all required models on Hugging Face
3. Your account has appropriate access to the pyannote models

### SpeechBrain Warning Messages

You may see the following warning when running the development server:
```
Module 'speechbrain.pretrained' was deprecated, redirecting to 'speechbrain.inference'
```

This warning is benign and is related to a SpeechBrain 1.0 change where they moved functionality from `speechbrain.pretrained` to `speechbrain.inference`. The warning has been suppressed in the following ways:

1. In production mode: The warning is handled in wsgi.py
2. In development mode: The warning is suppressed when using the run_dev.sh script
3. Directly in the code: A warnings.filterwarnings() statement has been added

### GPU Memory Issues

The API is configured to run efficiently on an NVIDIA GPU with 20GB VRAM. If you're running on a different GPU configuration:

1. For GPUs with less memory: Reduce the `batch_size` parameter in the transcription function (currently set to 16)
2. For better performance on high-memory GPUs: Increase the `batch_size` parameter for faster processing

You can monitor GPU memory usage by:
1. Checking the `/health` endpoint
2. Using the included `monitor.py` script
3. Running `nvidia-smi` in a terminal

### Server Connection Issues

If you can't connect to the API:

1. Make sure the server is running (check for gunicorn processes)
2. Verify the port is correct (default is 8000)
3. Check if there are any firewall issues blocking the connection
4. Look at the server logs for any errors

### Testing and Debugging

The included test_client.py script offers multiple options for testing:

```bash
# Basic options
python test_client.py --audio /path/to/file.wav

# Full options
python test_client.py \
  --audio /path/to/file.wav \
  --language en \
  --no-diarization \
  --min-speakers 1 \
  --max-speakers 5 \
  --port 8000
```

You can also use the monitor.py script for real-time monitoring:

```bash
# Basic monitoring dashboard
./monitor.py

# Continuous monitoring (auto-refresh)
./monitor.py --continuous --interval 5

# Get JSON output
./monitor.py --json > api_status.json
```
