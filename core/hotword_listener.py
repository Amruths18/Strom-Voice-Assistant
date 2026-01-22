"""
Enhanced Hotword Listener Module for Strom AI Assistant
Detects wake word ("Hey Storm") and stop word ("Stop Storm")
"""

import json
import queue
import sys
import time
from vosk import Model, KaldiRecognizer
import pyaudio
from typing import Callable, Optional
import numpy as np


class HotwordListener:
    """
    Listens for wake word and stop word using offline speech recognition.
    """
    
    def __init__(
        self,
        wake_word: str = "hey storm",
        stop_word: str = "stop storm",
        model_path: str = "model",
        sample_rate: int = 16000,
        chunk_size: int = 4000
    ):
        """Initialize the hotword listener."""
        self.wake_word = wake_word.lower()
        self.stop_word = stop_word.lower()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.is_listening = False
        self.is_active = False
        
        print(f"[Hotword] Initializing...")
        print(f"[Hotword] Wake word: '{self.wake_word}'")
        print(f"[Hotword] Stop word: '{self.stop_word}'")
        
        # Audio configuration
        self.audio_queue = queue.Queue()
        
        # Initialize Vosk model
        try:
            print(f"[Hotword] Loading Vosk model from: {model_path}")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
            print(f"[Hotword] ✅ Vosk model loaded successfully")
        except Exception as e:
            print(f"[Hotword] ❌ ERROR: Failed to load Vosk model")
            print(f"[Hotword] Path: {model_path}")
            print(f"[Hotword] Error: {str(e)}")
            print("\n[Hotword] SOLUTION:")
            print("  1. Download: https://alphacephei.com/vosk/models")
            print("  2. Get: vosk-model-small-en-us-0.15")
            print("  3. Extract to project root as 'model' folder")
            sys.exit(1)
        
        # PyAudio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # List and select input device
        self._list_audio_devices()
        self.input_device_index = self._get_best_input_device()
    
    def _list_audio_devices(self):
        """List all available audio input devices."""
        print("\n[Hotword] Available audio input devices:")
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        input_devices = []
        for i in range(num_devices):
            try:
                device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
                if device_info.get('maxInputChannels') > 0:
                    input_devices.append(device_info)
                    is_default = ""
                    try:
                        default = self.audio.get_default_input_device_info()
                        if i == default['index']:
                            is_default = " ⭐ (DEFAULT)"
                    except:
                        pass
                    print(f"  [{i}] {device_info.get('name')}{is_default}")
            except:
                pass
        
        if not input_devices:
            print("  ❌ No input devices found!")
        print()
    
    def _get_best_input_device(self) -> Optional[int]:
        """Get the best available input device."""
        try:
            default_device = self.audio.get_default_input_device_info()
            print(f"[Hotword] Using: {default_device['name']}")
            return default_device['index']
        except:
            print("[Hotword] ⚠️ No default device, trying first available...")
            info = self.audio.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            for i in range(num_devices):
                try:
                    device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
                    if device_info.get('maxInputChannels') > 0:
                        print(f"[Hotword] Using: {device_info['name']}")
                        return i
                except:
                    pass
            
            print("[Hotword] ❌ No input devices available!")
            return None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for PyAudio stream."""
        if status:
            print(f"[Hotword] Status: {status}")
        self.audio_queue.put(bytes(in_data))
        return (None, pyaudio.paContinue)
    
    def start_listening(self):
        """Start audio stream for hotword detection."""
        if self.is_listening:
            return
        
        if self.input_device_index is None:
            print("[Hotword] ❌ Cannot start: No input device")
            return
        
        try:
            print("[Hotword] Starting audio stream...")
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            self.is_listening = True
            print("[Hotword] ✅ Listening...")
        except Exception as e:
            print(f"[Hotword] ❌ Failed to start: {str(e)}")
            print("\nSOLUTIONS:")
            print("  1. Check microphone connection")
            print("  2. Check system permissions")
            print("  3. Close other apps using microphone")
            sys.exit(1)
    
    def stop_listening(self):
        """Stop audio stream."""
        if not self.is_listening:
            return
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.is_listening = False
        print("[Hotword] Stopped.")
    
    def detect_hotword(self) -> Optional[str]:
        """Detect wake/stop words. Returns 'wake', 'stop', or None."""
        if self.audio_queue.empty():
            return None
        
        try:
            data = self.audio_queue.get()
            
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').lower().strip()
                
                if text:
                    # Debug: show what was heard
                    if len(text) > 0:
                        print(f"[Hotword] Heard: '{text}'")
                    
                    # Check for wake word with fuzzy matching
                    if self._contains_wake_word(text):
                        print(f"[Hotword] ✅ WAKE WORD DETECTED!")
                        return 'wake'
                    
                    # Check for stop word with fuzzy matching
                    if self._contains_stop_word(text):
                        print(f"[Hotword] ✅ STOP WORD DETECTED!")
                        return 'stop'
        except Exception as e:
            print(f"[Hotword] Error: {str(e)}")
        
        return None
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains wake word with fuzzy matching."""
        text_words = set(text.split())
        wake_words = set(self.wake_word.split())

        # Exact match
        if self.wake_word in text:
            return True

        # Fuzzy match - check if most wake words are present
        common_words = wake_words.intersection(text_words)
        if len(common_words) >= len(wake_words) * 0.5:  # 50% match
            return True

        return False
    
    def _contains_stop_word(self, text: str) -> bool:
        """Check if text contains stop word with fuzzy matching."""
        text_words = set(text.split())
        stop_words = set(self.stop_word.split())

        # Exact match
        if self.stop_word in text:
            return True

        # Fuzzy match - check if most stop words are present
        common_words = stop_words.intersection(text_words)
        if len(common_words) >= len(stop_words) * 0.5:  # 50% match
            return True

        return False
    
    def listen_loop(
        self, 
        on_wake: Optional[Callable] = None,
        on_stop: Optional[Callable] = None
    ):
        """Main listening loop."""
        self.start_listening()
        
        try:
            print(f"\n{'='*60}")
            print(f"  🎤 Say '{self.wake_word}' to activate")
            print(f"  🛑 Say '{self.stop_word}' to deactivate")
            print(f"  ⌨️  Press Ctrl+C to exit")
            print(f"{'='*60}\n")
            
            while True:
                detection = self.detect_hotword()
                
                if detection == 'wake' and not self.is_active:
                    self.is_active = True
                    print("[Hotword] 🟢 ACTIVE")
                    if on_wake:
                        on_wake()
                
                elif detection == 'stop' and self.is_active:
                    self.is_active = False
                    print("[Hotword] 🔴 INACTIVE")
                    if on_stop:
                        on_stop()
                
                time.sleep(0.01)
                        
        except KeyboardInterrupt:
            print("\n[Hotword] Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_listening()
        if self.audio:
            self.audio.terminate()
        print("[Hotword] Cleaned up.")


if __name__ == "__main__":
    listener = HotwordListener()
    listener.listen_loop()