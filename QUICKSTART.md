# WhisperX API Quick Start Guide

This guide provides the essential steps to quickly get the WhisperX API up and running.

## Pre-requisites

- Python 3.8+ installed
- NVIDIA GPU with CUDA 12.8 support
- 20GB+ VRAM (for large-v3 model)
- PyTorch 2.7.0
- Hugging Face account and access token

## 1. Clone and Setup

```bash
# Navigate to your project directory
cd llm

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure the API

```bash
# Create and edit .env file
cp .env.example .env
```

Edit the `.env` file and add your Hugging Face token:

```
HF_TOKEN=your_huggingface_token_here
```

## 3. Make Scripts Executable

```bash
chmod +x run_dev.sh
chmod +x start.sh
chmod +x monitor.py
```

## 4. Verify Hugging Face Access

```bash
python check_hf_access.py
```

If you see any "Access denied" messages, visit the provided URLs to accept the model terms.

## 5. Start the API

For development:
```bash
./run_dev.sh
```

For production:
```bash
./start.sh
```

## 6. Test the API

```bash
# Test basic connectivity
python test_client.py

# Test transcription with your audio file
python test_client.py --audio /path/to/your/audio.wav
```

## 7. Monitor the API

```bash
./monitor.py
```

## 8. Use the API

Send requests to the following endpoints:

- Health check: `GET http://localhost:8000/health`
- Models info: `GET http://localhost:8000/models/info`
- Transcribe audio: `POST http://localhost:8000/transcribe`

Example transcription request:

```bash
curl -X POST http://localhost:8000/transcribe \
  -F "audio=@/path/to/audio.mp3" \
  -F "diarization=true" \
  -F "language=en"
```

## Troubleshooting

- If you see "module not found" errors, check your virtual environment activation
- If you get GPU memory errors, try reducing batch_size in app.py
- For connection issues, check if the server is running on the correct port
- If models fail to load, verify your Hugging Face token permissions

For more details, refer to the full README.md file.