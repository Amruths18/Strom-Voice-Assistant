"""
Text-to-Speech Module for Strom AI Assistant
Converts text responses to voice output using pyttsx3 (offline).
Provides natural, conversational voice responses.
"""

import pyttsx3
from typing import Optional


class TextToSpeech:
    """
    Handles text-to-speech conversion using pyttsx3 for offline voice synthesis.
    Configurable voice, rate, and volume settings.
    """
    
    def __init__(
        self,
        rate: int = 150,
        volume: float = 0.9,
        voice_gender: str = "female"
    ):
        """
        Initialize Text-to-Speech engine.
        
        Args:
            rate: Speech rate (words per minute). Default: 150
            volume: Volume level (0.0 to 1.0). Default: 0.9
            voice_gender: Preferred voice gender ("male" or "female")
        """
        self.rate = rate
        self.volume = volume
        self.voice_gender = voice_gender.lower()
        
        # Initialize pyttsx3 engine
        try:
            self.engine = pyttsx3.init()
            print("[TTS] Text-to-Speech engine initialized.")
        except Exception as e:
            print(f"[TTS] ERROR: Failed to initialize TTS engine: {str(e)}")
            self.engine = None
            return
        
        # Configure speech properties
        self._configure_voice()
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
        
    def _configure_voice(self):
        """Select and configure the voice based on gender preference."""
        if not self.engine:
            return
        
        voices = self.engine.getProperty('voices')
        
        # Try to find preferred gender voice
        selected_voice = None
        
        for voice in voices:
            voice_name = voice.name.lower()
            
            if self.voice_gender == "female":
                if "female" in voice_name or "zira" in voice_name or "hazel" in voice_name:
                    selected_voice = voice.id
                    break
            elif self.voice_gender == "male":
                if "male" in voice_name or "david" in voice_name or "mark" in voice_name:
                    selected_voice = voice.id
                    break
        
        # Fallback to first available voice
        if not selected_voice and voices:
            selected_voice = voices[0].id
        
        if selected_voice:
            self.engine.setProperty('voice', selected_voice)
            print(f"[TTS] Voice configured: {self.voice_gender}")
        else:
            print("[TTS] WARNING: Could not configure voice.")
    
    def speak(self, text: str, wait: bool = True):
        """
        Convert text to speech and play audio.
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete before returning
        """
        if not self.engine:
            print("[TTS] ERROR: TTS engine not initialized.")
            return
        
        if not text or not text.strip():
            print("[TTS] WARNING: Empty text provided.")
            return
        
        try:
            print(f"[TTS] Speaking: \"{text}\"")
            
            if wait:
                # Blocking mode: wait for speech to complete
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # Non-blocking mode: speak in background
                self.engine.say(text)
                self.engine.startLoop(False)
                self.engine.iterate()
                self.engine.endLoop()
                
        except Exception as e:
            print(f"[TTS] ERROR during speech: {str(e)}")
    
    def set_rate(self, rate: int):
        """
        Change speech rate.
        
        Args:
            rate: New speech rate (words per minute)
        """
        if self.engine:
            self.rate = rate
            self.engine.setProperty('rate', rate)
            print(f"[TTS] Speech rate set to: {rate} WPM")
    
    def set_volume(self, volume: float):
        """
        Change volume level.
        
        Args:
            volume: New volume level (0.0 to 1.0)
        """
        if self.engine:
            volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
            self.volume = volume
            self.engine.setProperty('volume', volume)
            print(f"[TTS] Volume set to: {volume}")
    
    def stop(self):
        """Stop current speech immediately."""
        if self.engine:
            try:
                self.engine.stop()
                print("[TTS] Speech stopped.")
            except Exception as e:
                print(f"[TTS] ERROR stopping speech: {str(e)}")
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices on the system.
        
        Returns:
            List of voice information dictionaries
        """
        if not self.engine:
            return []
        
        voices = self.engine.getProperty('voices')
        voice_list = []
        
        for voice in voices:
            voice_info = {
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages,
                'gender': voice.gender if hasattr(voice, 'gender') else 'unknown'
            }
            voice_list.append(voice_info)
        
        return voice_list
    
    def cleanup(self):
        """Clean up TTS engine resources."""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        print("[TTS] Resources cleaned up.")


# Test function for standalone execution
def _test_text_to_speech():
    """Test the text-to-speech module independently."""
    
    print("=== Strom TTS Module Test ===")
    
    # Initialize TTS
    tts = TextToSpeech(
        rate=150,
        volume=0.9,
        voice_gender="female"
    )
    
    # List available voices
    print("\n📢 Available Voices:")
    voices = tts.get_available_voices()
    for i, voice in enumerate(voices, 1):
        print(f"  {i}. {voice['name']} ({voice.get('gender', 'unknown')})")
    
    # Test speech
    print("\n🔊 Testing speech output...")
    test_phrases = [
        "Hello! I am Strom, your personal AI assistant.",
        "I can help you with system control, reminders, and much more.",
        "Let me know how I can assist you today!"
    ]
    
    try:
        for phrase in test_phrases:
            tts.speak(phrase, wait=True)
        
        print("\n✅ TTS Test Complete!")
        
    except KeyboardInterrupt:
        print("\n[TTS] Test interrupted.")
    finally:
        tts.cleanup()


if __name__ == "__main__":
    _test_text_to_speech()