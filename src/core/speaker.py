# File: src/core/speaker.py
import pyttsx3
from src.config import VOICE_RATE

engine = pyttsx3.init()
engine.setProperty('rate', VOICE_RATE)

def speak(text):
    """Converts text to speech output"""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()