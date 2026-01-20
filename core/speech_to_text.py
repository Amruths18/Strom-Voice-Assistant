"""
Speech-to-Text Module for Strom AI Assistant
Converts voice input to text using offline (Vosk) and optional online (Whisper API) methods.
Automatically detects network status and chooses appropriate method.
"""

import json
import pyaudio
import wave
import os
import sys
from vosk import KaldiRecognizer
from typing import Optional
from core.vosk_manager import get_vosk_model
import requests
import tempfile


class SpeechToText:
    """
    Handles speech-to-text conversion with offline-first approach.
    Falls back to Vosk if online services are unavailable.
    """
    
    def __init__(
        self,
        model_path: str = "model",
        sample_rate: int = 16000,
        whisper_api_key: Optional[str] = None,
        use_online: bool = True
    ):
        """
        Initialize Speech-to-Text engine.
        
        Args:
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate in Hz
            whisper_api_key: OpenAI API key for Whisper (optional)
            use_online: Whether to attempt online STT when available
        """
        self.sample_rate = sample_rate
        self.whisper_api_key = whisper_api_key
        self.use_online = use_online
        self.chunk_size = 4000
        
        # Initialize Vosk for offline recognition (use cached model)
        try:
            self.model = get_vosk_model(model_path)
            print(f"[STT] Vosk model (cached) loaded from: {model_path}")
        except Exception as e:
            print(f"[STT] ERROR: Failed to load Vosk model from '{model_path}'")
            print(f"[STT] {str(e)}")
            sys.exit(1)
        
        # PyAudio setup
        self.audio = pyaudio.PyAudio()
        
    def is_online(self) -> bool:
        """
        Check if internet connection is available.
        
        Returns:
            True if online, False otherwise
        """
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def record_audio(self, duration: int = 5, silence_threshold: int = 500) -> str:
        """
        Record audio from microphone and save to temporary file.
        
        Args:
            duration: Maximum recording duration in seconds
            silence_threshold: Threshold for silence detection
            
        Returns:
            Path to recorded audio file
        """
        print("[STT] Listening... Speak now!")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        frames = []
        
        # Record audio
        for i in range(0, int(self.sample_rate / self.chunk_size * duration)):
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        wf = wave.open(temp_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print("[STT] Recording complete.")
        return temp_path
    
    def transcribe_offline(self, audio_path: str) -> str:
        """
        Transcribe audio file using Vosk (offline).
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            recognizer = KaldiRecognizer(self.model, self.sample_rate)
            recognizer.SetWords(True)
            
            wf = wave.open(audio_path, "rb")
            
            # Process audio in chunks
            full_text = ""
            while True:
                data = wf.readframes(self.chunk_size)
                if len(data) == 0:
                    break
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    full_text += result.get('text', '') + " "
            
            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            full_text += final_result.get('text', '')
            
            wf.close()
            
            return full_text.strip()
            
        except Exception as e:
            print(f"[STT] Offline transcription error: {str(e)}")
            return ""
    
    def transcribe_online(self, audio_path: str) -> str:
        """
        Transcribe audio file using Whisper API (online).
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not self.whisper_api_key:
            print("[STT] No Whisper API key provided. Using offline mode.")
            return self.transcribe_offline(audio_path)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.whisper_api_key}"
            }
            
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': audio_file,
                    'model': (None, 'whisper-1')
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '').strip()
            else:
                print(f"[STT] Online transcription failed: {response.status_code}")
                print("[STT] Falling back to offline mode.")
                return self.transcribe_offline(audio_path)
                
        except Exception as e:
            print(f"[STT] Online transcription error: {str(e)}")
            print("[STT] Falling back to offline mode.")
            return self.transcribe_offline(audio_path)
    
    def listen_and_transcribe(self, duration: int = 5) -> str:
        """
        Main method: Record audio and transcribe to text.
        Automatically chooses online or offline mode based on availability.
        
        Args:
            duration: Maximum recording duration in seconds
            
        Returns:
            Transcribed text
        """
        # Record audio
        audio_path = self.record_audio(duration=duration)
        
        # Determine transcription method
        online_available = self.use_online and self.is_online() and self.whisper_api_key
        
        if online_available:
            print("[STT] Using online transcription (Whisper API)")
            text = self.transcribe_online(audio_path)
        else:
            print("[STT] Using offline transcription (Vosk)")
            text = self.transcribe_offline(audio_path)
        
        # Clean up temporary file
        try:
            os.remove(audio_path)
        except:
            pass
        
        if text:
            print(f"[STT] Transcribed: \"{text}\"")
        else:
            print("[STT] No speech detected or transcription failed.")
        
        return text
    
    def cleanup(self):
        """Clean up resources."""
        if self.audio:
            self.audio.terminate()
        print("[STT] Resources cleaned up.")


# Test function for standalone execution
def _test_speech_to_text():
    """Test the speech-to-text module independently."""
    
    print("=== Strom STT Module Test ===")
    print("This will test offline speech recognition.")
    print("Speak after you see 'Listening...'")
    
    # Initialize STT (offline only for testing)
    stt = SpeechToText(
        model_path="model",
        use_online=False
    )
    
    try:
        # Test transcription
        text = stt.listen_and_transcribe(duration=5)
        
        if text:
            print(f"\n✅ Success! You said: \"{text}\"")
        else:
            print("\n❌ Failed to transcribe audio.")
            
    except KeyboardInterrupt:
        print("\n[STT] Test interrupted.")
    finally:
        stt.cleanup()


if __name__ == "__main__":
    _test_speech_to_text()
