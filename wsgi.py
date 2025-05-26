import warnings

# Filter out specific SpeechBrain deprecation warning
warnings.filterwarnings("ignore", message="Module 'speechbrain.pretrained' was deprecated")

from app import app, load_models

if __name__ == "__main__":
    # Load models when starting with Gunicorn
    load_models()
    app.run()
else:
    # Load models when imported by Gunicorn
    load_models()
