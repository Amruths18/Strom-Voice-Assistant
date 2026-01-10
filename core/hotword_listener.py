"""
Hotword Listener Module for Strom AI Assistant
Detects wake word ("Hey Strom") and stop word ("Stop Strom") using Vosk offline speech recognition.
Runs in a continuous loop and signals when user wants to activate or stop the assistant.
"""

import json
import queue
import sys
from vosk import Model, KaldiRecognizer
import pyaudio
import threading
from typing import Callable, Optional


class HotwordListener:
    """
    Listens for wake word and stop word using offline speech recognition.
    Uses Vosk for accurate, low-latency hotword detection.
    """
    
    def __init__(
        self, 
        wake_word: str = "hey strom",
        stop_word: str = "stop strom",
        model_path: str = "model",
        sample_rate: int = 16000
    ):
        """
        Initialize the hotword listener.
        
        Args:
            wake_word: Phrase to activate Strom (default: "hey strom")
            stop_word: Phrase to stop Strom (default: "stop strom")
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate in Hz
        """
        self.wake_word = wake_word.lower()
        self.stop_word = stop_word.lower()
        self.sample_rate = sample_rate
        self.is_listening = False
        self.is_active = False
        
        # Audio configuration
        self.chunk_size = 4000
        self.audio_queue = queue.Queue()
        
        # Initialize Vosk model
        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)
            print(f"[Hotword] Vosk model loaded from: {model_path}")
        except Exception as e:
            print(f"[Hotword] ERROR: Failed to load Vosk model from '{model_path}'")
            print(f"[Hotword] {str(e)}")
            print("[Hotword] Please download a Vosk model from https://alphacephei.com/vosk/models")
            sys.exit(1)
        
        # PyAudio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for PyAudio stream to capture audio data."""
        self.audio_queue.put(bytes(in_data))
        return (None, pyaudio.paContinue)
    
    def start_listening(self):
        """Start the audio stream for hotword detection."""
        if self.is_listening:
            return
        
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            self.is_listening = True
            print("[Hotword] Microphone activated. Listening for wake word...")
        except Exception as e:
            print(f"[Hotword] ERROR: Failed to start audio stream: {str(e)}")
            sys.exit(1)
    
    def stop_listening(self):
        """Stop the audio stream."""
        if not self.is_listening:
            return
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.is_listening = False
        print("[Hotword] Microphone deactivated.")
    
    def detect_hotword(self) -> Optional[str]:
        """
        Process audio queue and detect wake/stop words.
        
        Returns:
            'wake' if wake word detected
            'stop' if stop word detected
            None if no hotword detected
        """
        if self.audio_queue.empty():
            return None
        
        # Process available audio data
        data = self.audio_queue.get()
        
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            text = result.get('text', '').lower().strip()
            
            if text:
                # Check for wake word
                if self.wake_word in text:
                    print(f"[Hotword] Wake word detected: '{text}'")
                    return 'wake'
                
                # Check for stop word
                if self.stop_word in text:
                    print(f"[Hotword] Stop word detected: '{text}'")
                    return 'stop'
        
        return None
    
    def listen_loop(
        self, 
        on_wake: Optional[Callable] = None,
        on_stop: Optional[Callable] = None
    ):
        """
        Main listening loop that continuously monitors for hotwords.
        
        Args:
            on_wake: Callback function to execute when wake word detected
            on_stop: Callback function to execute when stop word detected
        """
        self.start_listening()
        
        try:
            print(f"[Hotword] Say '{self.wake_word}' to activate Strom")
            print(f"[Hotword] Say '{self.stop_word}' to deactivate Strom")
            print("[Hotword] Press Ctrl+C to exit")
            
            while True:
                detection = self.detect_hotword()
                
                if detection == 'wake' and not self.is_active:
                    self.is_active = True
                    print("[Hotword] Strom is now ACTIVE")
                    if on_wake:
                        on_wake()
                
                elif detection == 'stop' and self.is_active:
                    self.is_active = False
                    print("[Hotword] Strom is now INACTIVE")
                    if on_stop:
                        on_stop()
                        
        except KeyboardInterrupt:
            print("\n[Hotword] Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_listening()
        if self.audio:
            self.audio.terminate()
        print("[Hotword] Resources cleaned up.")


# Test function for standalone execution
def _test_hotword_listener():
    """Test the hotword listener independently."""
    
    def on_wake_detected():
        print(">>> WAKE CALLBACK TRIGGERED <<<")
    
    def on_stop_detected():
        print(">>> STOP CALLBACK TRIGGERED <<<")
    
    # Initialize listener
    listener = HotwordListener(
        wake_word="hey strom",
        stop_word="stop strom",
        model_path="model"  # Update this path to your Vosk model location
    )
    
    # Start listening loop
    listener.listen_loop(
        on_wake=on_wake_detected,
        on_stop=on_stop_detected
    )


if __name__ == "__main__":
    _test_hotword_listener()