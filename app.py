import os
import tempfile
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import whisperx
import gc
import torch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Global variables for models
whisperx_model = None
align_model = None
align_metadata = None
diarize_pipeline = None

# Supported audio formats
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4', 'avi', 'mov', 'mkv', 'flac', 'm4a', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_models():
    """Load WhisperX models on startup"""
    global whisperx_model, align_model, align_metadata, diarize_pipeline
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    
    logger.info(f"Loading models on device: {device}")
    
    try:
        # Load WhisperX model
        whisperx_model = whisperx.load_model("large-v2", device, compute_type=compute_type)
        logger.info("WhisperX model loaded successfully")
        
        # Load alignment model
        align_model, align_metadata = whisperx.load_align_model(language_code="en", device=device)
        logger.info("Alignment model loaded successfully")
        
        # Load diarization model
        # Check for both HUGGINGFACE_TOKEN and HF_TOKEN
        hf_token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
        if hf_token:
            # Correct way to initialize the diarization model in WhisperX
            from pyannote.audio import Pipeline
            diarize_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                                       use_auth_token=hf_token)
            if torch.cuda.is_available():
                diarize_pipeline = diarize_pipeline.to(torch.device(device))
            logger.info("Diarization model loaded successfully")
        else:
            logger.warning("HF_TOKEN not found, diarization will be disabled")
            
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'whisperx_loaded': whisperx_model is not None,
        'align_loaded': align_model is not None,
        'diarize_loaded': diarize_pipeline is not None,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'gpu_memory': torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else None
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Main transcription endpoint with optional diarization"""
    try:
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400
        
        # Get optional parameters
        enable_diarization = request.form.get('diarization', 'false').lower() == 'true'
        language = request.form.get('language', 'en')
        min_speakers = int(request.form.get('min_speakers', 1))
        max_speakers = int(request.form.get('max_speakers', 10))
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            # Load audio
            audio = whisperx.load_audio(temp_path)
            logger.info(f"Processing audio file: {filename}")
            
            # Transcribe
            result = whisperx_model.transcribe(audio, batch_size=16, language=language)
            
            # Align
            if align_model:
                result = whisperx.align(result["segments"], align_model, align_metadata, audio, device="cuda" if torch.cuda.is_available() else "cpu", return_char_alignments=False)
            
            # Diarize if requested and model is available
            if enable_diarization and diarize_pipeline:
                # Correct way to use the diarization model with WhisperX
                diarize_segments = whisperx.diarize(audio, diarize_pipeline, min_speakers=min_speakers, max_speakers=max_speakers)
                result = whisperx.assign_word_speakers(diarize_segments, result)
            
            # Clean up GPU memory
            gc.collect()
            torch.cuda.empty_cache()
            
            return jsonify({
                'success': True,
                'transcription': result,
                'filename': filename,
                'diarization_enabled': enable_diarization and diarize_pipeline is not None
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models/info', methods=['GET'])
def models_info():
    """Get information about loaded models"""
    return jsonify({
        'whisperx_model': 'large-v2' if whisperx_model else None,
        'align_model_loaded': align_model is not None,
        'diarization_available': diarize_pipeline is not None,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    load_models()
    app.run(debug=True, host='0.0.0.0', port=5000)
