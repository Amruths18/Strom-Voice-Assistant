# File: src/core/listener.py
import os
import sys
import json
import pyaudio
from vosk import Model, KaldiRecognizer
from src.config import MODEL_PATH

# Check if model exists
if not os.path.exists(MODEL_PATH):
    print(f"ERROR: Model not found at {MODEL_PATH}")
    print("Please download the model from https://alphacephei.com/vosk/models and unpack it in assets/models/")
    sys.exit(1)

# Initialize Model
print("Initializing Offline Model...")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

def listen():
    """Listens for audio and returns text"""
    print("Listening...")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result['text']
            if text:
                print(f"User: {text}")
                return text.lower()