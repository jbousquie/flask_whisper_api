import requests
import json

def test_health():
    """Test the health endpoint"""
    response = requests.get('http://localhost:8000/health')
    print("Health Check:", response.json())

def test_transcription(audio_file_path):
    """Test transcription with an audio file"""
    url = 'http://localhost:8000/transcribe'
    
    with open(audio_file_path, 'rb') as f:
        files = {'audio': f}
        data = {
            'diarization': 'true',
            'language': 'en',
            'min_speakers': 1,
            'max_speakers': 5
        }
        
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        result = response.json()
        print("Transcription successful!")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_models_info():
    """Test the models info endpoint"""
    response = requests.get('http://localhost:8000/models/info')
    print("Models Info:", response.json())

if __name__ == "__main__":
    # Test endpoints
    test_health()
    test_models_info()
    
    # Uncomment and provide an audio file path to test transcription
    # test_transcription('/path/to/your/audio/file.wav')
