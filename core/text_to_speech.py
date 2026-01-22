"""
Text-to-Speech Module for Strom AI Assistant
"""

import pyttsx3
from typing import Optional


class TextToSpeech:
    """
    Handles text-to-speech conversion using pyttsx3.
    """
    
    def __init__(
        self,
        rate: int = 150,
        volume: float = 0.9,
        voice_gender: str = "female"
    ):
        """Initialize TTS engine."""
        self.rate = rate
        self.volume = volume
        self.voice_gender = voice_gender.lower()
        
        try:
            self.engine = pyttsx3.init()
            print("[TTS] Initialized")
        except Exception as e:
            print(f"[TTS] ❌ Failed: {str(e)}")
            self.engine = None
            return
        
        self._configure_voice()
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
    
    def _configure_voice(self):
        """Select voice based on gender."""
        if not self.engine:
            return
        
        voices = self.engine.getProperty('voices')
        selected = None
        
        for voice in voices:
            name = voice.name.lower()
            
            if self.voice_gender == "female":
                if any(word in name for word in ["female", "zira", "hazel"]):
                    selected = voice.id
                    break
            elif self.voice_gender == "male":
                if any(word in name for word in ["male", "david", "mark"]):
                    selected = voice.id
                    break
        
        if not selected and voices:
            selected = voices[0].id
        
        if selected:
            self.engine.setProperty('voice', selected)
            print(f"[TTS] Voice: {self.voice_gender}")
    
    def speak(self, text: str, wait: bool = True):
        """Convert text to speech with enhanced error handling."""
        if not self.engine or not text:
            print(f"[TTS] ⚠️ Cannot speak: {'No engine' if not self.engine else 'No text'}")
            return
        
        try:
            print(f"[TTS] Speaking: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # Clear any pending speech
            self.engine.stop()
            
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
                print("[TTS] ✅ Speech completed")
            else:
                print("[TTS] 🔄 Speech queued")
                
        except Exception as e:
            print(f"[TTS] ❌ Error: {str(e)}")
            # Try to reinitialize engine
            try:
                self._reinitialize_engine()
                print("[TTS] 🔄 Retrying...")
                self.engine.say(text)
                if wait:
                    self.engine.runAndWait()
            except Exception as e2:
                print(f"[TTS] ❌ Recovery failed: {str(e2)}")
    
    def _reinitialize_engine(self):
        """Reinitialize TTS engine."""
        try:
            if self.engine:
                self.engine.stop()
            self.engine = pyttsx3.init()
            self._configure_voice()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            print("[TTS] 🔄 Engine reinitialized")
        except Exception as e:
            print(f"[TTS] ❌ Reinitialization failed: {str(e)}")
            self.engine = None
    
    def cleanup(self):
        """Clean up."""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak("Hello! I am Strom, your AI assistant.")
    tts.cleanup()