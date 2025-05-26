import requests
import json
import argparse
import sys
import os
import time

# Base URL for the API
API_BASE_URL = 'http://localhost:8000'

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f'{API_BASE_URL}/health', timeout=10)
        response.raise_for_status()
        result = response.json()
        print("\n=== Health Check ===")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Device: {result.get('device', 'unknown')}")
        print(f"WhisperX loaded: {result.get('whisperx_loaded', False)}")
        print(f"Align loaded: {result.get('align_loaded', False)}")
        print(f"Diarize loaded: {result.get('diarize_loaded', False)}")
        if result.get('gpu_memory'):
            print(f"GPU Memory: {result.get('gpu_memory'):.2f} GB")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Health check failed: {str(e)}")
        return False

def test_transcription(audio_file_path, language='en', diarization=True, min_speakers=1, max_speakers=5):
    """Test transcription with an audio file"""
    if not os.path.exists(audio_file_path):
        print(f"\n❌ Error: Audio file not found at {audio_file_path}")
        return False
    
    print(f"\n=== Transcribing {os.path.basename(audio_file_path)} ===")
    print(f"Language: {language}, Diarization: {diarization}")
    print(f"Speaker range: {min_speakers}-{max_speakers}")
    
    url = f'{API_BASE_URL}/transcribe'
    
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'audio': (os.path.basename(audio_file_path), f)}
            data = {
                'diarization': 'true' if diarization else 'false',
                'language': language,
                'min_speakers': min_speakers,
                'max_speakers': max_speakers
            }
            
            print("Sending request to server...")
            start_time = time.time()
            
            response = requests.post(url, files=files, data=data, timeout=300)  # 5-minute timeout
            
            elapsed_time = time.time() - start_time
            print(f"Processing time: {elapsed_time:.2f} seconds")
            
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Transcription successful!")
            
            # Print transcript summary
            if 'transcription' in result and 'segments' in result['transcription']:
                segments = result['transcription']['segments']
                total_segments = len(segments)
                word_count = sum(len(segment.get('words', [])) for segment in segments)
                
                print(f"\nTotal segments: {total_segments}")
                print(f"Total words: {word_count}")
                
                # Print first few segments as a sample
                print("\n=== Sample Transcript ===")
                for i, segment in enumerate(segments[:3]):
                    speaker = segment.get('speaker', 'unknown')
                    text = segment.get('text', '')
                    print(f"[Speaker {speaker}]: {text}")
                    
                    if i >= 2 and len(segments) > 3:
                        print(f"... {total_segments - 3} more segments ...")
                        break
            
            # Ask if user wants to see the full JSON output
            if input("\nShow full JSON output? (y/n): ").lower() == 'y':
                print(json.dumps(result, indent=2))
                
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Transcription request failed: {str(e)}")
        return False

def test_models_info():
    """Test the models info endpoint"""
    try:
        response = requests.get(f'{API_BASE_URL}/models/info', timeout=10)
        response.raise_for_status()
        result = response.json()
        
        print("\n=== Models Info ===")
        print(f"WhisperX Model: {result.get('whisperx_model', 'Not loaded')}")
        print(f"Align Model: {'Loaded' if result.get('align_model_loaded') else 'Not loaded'}")
        print(f"Diarization: {'Available' if result.get('diarization_available') else 'Not available'}")
        print(f"Supported Formats: {', '.join(result.get('supported_formats', []))}")
        print(f"Max File Size: {result.get('max_file_size_mb', 0)} MB")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Models info check failed: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests except transcription"""
    success = True
    
    # Test API health
    if not test_health():
        success = False
    
    # Test models info
    if not test_models_info():
        success = False
        
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test WhisperX API endpoints')
    parser.add_argument('--audio', '-a', type=str, help='Path to audio file for transcription test')
    parser.add_argument('--language', '-l', type=str, default='en', help='Language code (default: en)')
    parser.add_argument('--no-diarization', action='store_true', help='Disable speaker diarization')
    parser.add_argument('--min-speakers', type=int, default=1, help='Minimum number of speakers (default: 1)')
    parser.add_argument('--max-speakers', type=int, default=5, help='Maximum number of speakers (default: 5)')
    parser.add_argument('--port', '-p', type=int, default=8000, help='API port (default: 8000)')
    
    args = parser.parse_args()
    
    # Update API base URL if port is changed
    if args.port != 8000:
        API_BASE_URL = f'http://localhost:{args.port}'
    
    print(f"\n🔍 Testing WhisperX API at {API_BASE_URL}")
    
    # Run basic tests
    if not run_all_tests():
        print("\n❌ Some tests failed. Check the API server status.")
        sys.exit(1)
    
    # Run transcription test if audio file is provided
    if args.audio:
        test_transcription(
            args.audio, 
            language=args.language,
            diarization=not args.no_diarization,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers
        )
    else:
        print("\n📝 To test transcription, run with:")
        print(f"python {os.path.basename(__file__)} --audio /path/to/audio/file.wav")
        
    print("\n✅ Testing complete")
