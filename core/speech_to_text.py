"""
Enhanced Speech-to-Text Module for Strom AI Assistant
Converts voice to text with silence detection
"""

import json
import pyaudio
import wave
import os
import sys
from vosk import Model, KaldiRecognizer
from typing import Optional
import requests
import tempfile
import numpy as np
import time


class SpeechToText:
    """
    Handles speech-to-text with offline/online support.
    """
    
    def __init__(
        self,
        model_path: str = "model",
        sample_rate: int = 16000,
        whisper_api_key: Optional[str] = None,
        use_online: bool = True,
        silence_threshold: int = 300,
        silence_duration: float = 1.5
    ):
        """Initialize STT engine."""
        self.sample_rate = sample_rate
        self.whisper_api_key = whisper_api_key
        self.use_online = use_online
        self.chunk_size = 4000
        
        # Enhanced silence detection parameters
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.min_speech_duration = 0.5  # Minimum speech to detect
        self.max_speech_duration = 15   # Maximum recording time
        
        # Audio preprocessing
        self.noise_reduction = True
        self.auto_gain = True
        
        # Initialize Vosk
        try:
            print(f"[STT] Loading Vosk model...")
            self.model = Model(model_path)
            print(f"[STT] ✅ Model loaded")
        except Exception as e:
            print(f"[STT] ❌ Failed to load model: {str(e)}")
            sys.exit(1)
        
        # PyAudio
        self.audio = pyaudio.PyAudio()
        self.input_device_index = self._get_input_device()
    
    def _get_input_device(self) -> Optional[int]:
        """Get input device."""
        try:
            device = self.audio.get_default_input_device_info()
            print(f"[STT] Using: {device['name']}")
            return device['index']
        except:
            return None
    
    def is_online(self) -> bool:
        """Check internet."""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def get_audio_level(self, data: bytes) -> float:
        """Calculate RMS audio level."""
        try:
            audio_data = np.frombuffer(data, dtype=np.int16)
            if len(audio_data) == 0:
                return 0.0
            
            # Calculate RMS, handle potential NaN/inf values
            rms = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
            return rms if np.isfinite(rms) else 0.0
        except:
            return 0.0
    
    def _detect_stop_command(self, audio_data: bytes) -> bool:
        """Detect stop command in audio data."""
        try:
            # Quick recognition for stop command
            temp_recognizer = KaldiRecognizer(self.model, self.sample_rate)
            temp_recognizer.SetWords(True)
            
            if temp_recognizer.AcceptWaveform(audio_data):
                result = json.loads(temp_recognizer.Result())
                text = result.get('text', '').lower().strip()
                
                # Check for stop words
                stop_words = ['stop', 'cancel', 'quit', 'exit', 'enough']
                for word in stop_words:
                    if word in text:
                        return True
            
            return False
        except:
            return False
    
    def record_audio_with_silence_detection(self, max_duration: int = 10) -> str:
        """Record audio with enhanced silence detection."""
        print("\n[STT] 🎤 Listening... Speak now! (Say 'stop' to cancel)")
        
        if self.input_device_index is None:
            print("[STT] ❌ No input device")
            return ""
        
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size
            )
        except Exception as e:
            print(f"[STT] ❌ Failed to open stream: {str(e)}")
            return ""
        
        frames = []
        silent_chunks = 0
        speech_chunks = 0
        chunks_per_second = self.sample_rate / self.chunk_size
        silence_threshold_chunks = int(self.silence_duration * chunks_per_second)
        min_speech_chunks = int(self.min_speech_duration * chunks_per_second)
        
        start_time = time.time()
        speech_detected = False
        noise_levels = []  # Track noise levels for dynamic threshold
        
        print("[STT] Level: ", end="", flush=True)
        print(f"\n[STT] Debug: Starting loop. Threshold: {self.silence_threshold}")
        
        try:
            while (time.time() - start_time) < self.max_speech_duration:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                level = self.get_audio_level(data)
                noise_levels.append(level)
                
                # Dynamic threshold adjustment based on recent noise
                if len(noise_levels) > 10:
                    noise_levels.pop(0)
                    avg_noise = sum(noise_levels) / len(noise_levels)
                else:
                    dynamic_threshold = self.silence_threshold
                
                # Debug logging every 10 chunks to avoid spamming but confirm liveness
                if len(frames) % 10 == 0:
                   print(f"\r[STT] Debug: Level={int(level)} Thresh={int(dynamic_threshold)} SpeechChunks={speech_chunks} SilentChunks={silent_chunks}  ", end="", flush=True)
                
                # Visual feedback
                bars = int(level / 200)  # Adjusted for better visualization
                status = "🎤" if level > dynamic_threshold else "🤫"
                print(f"\r[STT] {status} Level: {'█' * min(bars, 30)} {int(level):4d}", end="", flush=True)
                
                # Detect speech/silence
                if level > dynamic_threshold:
                    silent_chunks = 0
                    speech_chunks += 1
                    speech_detected = True
                else:
                    if speech_detected:
                        silent_chunks += 1
                
                # Stop on silence after minimum speech
                if speech_detected and speech_chunks >= min_speech_chunks and silent_chunks > silence_threshold_chunks:
                    print("\n[STT] ✅ Silence detected")
                    break
                
                # Check for stop command
                if len(frames) % 10 == 0:  # Check every ~0.4 seconds
                    recent_frames = frames[-10:] if len(frames) >= 10 else frames
                    if self._detect_stop_command(b"".join(recent_frames)):
                        print("\n[STT] 🛑 Stop command detected")
                        stream.stop_stream()
                        stream.close()
                        return ""
            
            print()
            
        except Exception as e:
            print(f"\n[STT] ❌ Recording error: {str(e)}")
            stream.stop_stream()
            stream.close()
            return ""
        
        stream.stop_stream()
        stream.close()
        
        if not speech_detected or speech_chunks < min_speech_chunks:
            print("[STT] ⚠️ No sufficient speech detected")
            return ""
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        wf = wave.open(temp_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        duration = len(frames) * self.chunk_size / self.sample_rate
        print(f"[STT] ✅ Recorded {duration:.1f}s audio")
        
        return temp_path
    
    def transcribe_offline(self, audio_path: str) -> str:
        """Transcribe with Vosk."""
        try:
            print("[STT] 🔄 Transcribing (offline)...")
            
            recognizer = KaldiRecognizer(self.model, self.sample_rate)
            recognizer.SetWords(True)
            
            wf = wave.open(audio_path, "rb")
            
            full_text = ""
            while True:
                data = wf.readframes(self.chunk_size)
                if len(data) == 0:
                    break
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '')
                    if text:
                        full_text += text + " "
            
            final = json.loads(recognizer.FinalResult())
            final_text = final.get('text', '')
            if final_text:
                full_text += final_text
            
            wf.close()
            
            text = full_text.strip()
            
            if text:
                print(f"[STT] ✅ '{text}'")
            else:
                print("[STT] ⚠️ No speech recognized")
            
            return text
            
        except Exception as e:
            print(f"[STT] ❌ Error: {str(e)}")
            return ""
    
    def transcribe_online(self, audio_path: str) -> str:
        """Transcribe with Whisper API."""
        if not self.whisper_api_key:
            return self.transcribe_offline(audio_path)
        
        try:
            print("[STT] 🔄 Transcribing (online)...")
            
            headers = {"Authorization": f"Bearer {self.whisper_api_key}"}
            
            with open(audio_path, 'rb') as f:
                files = {'file': f, 'model': (None, 'whisper-1')}
                
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                text = response.json().get('text', '').strip()
                if text:
                    print(f"[STT] ✅ '{text}'")
                return text
            else:
                print(f"[STT] ⚠️ Online failed, using offline")
                return self.transcribe_offline(audio_path)
                
        except Exception as e:
            print(f"[STT] ⚠️ Online error, using offline")
            return self.transcribe_offline(audio_path)
    
    def listen_and_transcribe(self, duration: int = 10) -> str:
        """Main method: record and transcribe."""
        audio_path = self.record_audio_with_silence_detection(max_duration=duration)
        
        if not audio_path:
            return ""
        
        # Choose method
        online_ok = self.use_online and self.is_online() and self.whisper_api_key
        
        if online_ok:
            text = self.transcribe_online(audio_path)
        else:
            text = self.transcribe_offline(audio_path)
        
        # Cleanup
        try:
            os.remove(audio_path)
        except:
            pass
        
        return text
    
    def cleanup(self):
        """Clean up."""
        if self.audio:
            self.audio.terminate()


if __name__ == "__main__":
    print("=== STT Test ===")
    stt = SpeechToText(use_online=False)
    
    try:
        text = stt.listen_and_transcribe()
        if text:
            print(f"\n✅ You said: '{text}'")
        else:
            print("\n❌ No text recognized")
    finally:
        stt.cleanup()