"""
Text-to-Speech Module for Strom AI Assistant
Converts text responses to voice output using pyttsx3 (offline).
Provides natural, conversational voice responses.
"""

import threading
import queue
import time
import pyttsx3
from typing import Optional, List


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
        
        # Background TTS worker will own the pyttsx3 engine
        self._task_queue: "queue.Queue" = queue.Queue()
        self._stop_event = threading.Event()
        self._ready_event = threading.Event()

        # Start worker thread
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

        # Enqueue setup task and wait briefly for initialization
        self._task_queue.put({'type': 'setup', 'rate': self.rate, 'volume': self.volume, 'voice_gender': self.voice_gender})
        self._ready_event.wait(timeout=5)
        
    def _configure_voice(self):
        """Select and configure the voice based on gender preference."""
        # Voice configuration is performed in the worker where the engine exists.
        return
    
    def speak(self, text: str, wait: bool = True):
        """
        Convert text to speech and play audio.
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete before returning
        """
        if not text or not text.strip():
            print("[TTS] WARNING: Empty text provided.")
            return

        if wait:
            done_event = threading.Event()
            self._task_queue.put({'type': 'speak', 'text': text, 'done_event': done_event})
            done_event.wait()
        else:
            self._task_queue.put({'type': 'speak', 'text': text, 'done_event': None})
    
    def set_rate(self, rate: int):
        """
        Change speech rate.
        
        Args:
            rate: New speech rate (words per minute)
        """
        self.rate = rate
        self._task_queue.put({'type': 'set_rate', 'rate': rate})
    
    def set_volume(self, volume: float):
        """
        Change volume level.
        
        Args:
            volume: New volume level (0.0 to 1.0)
        """
        volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
        self.volume = volume
        self._task_queue.put({'type': 'set_volume', 'volume': volume})
    
    def stop(self):
        """Stop current speech immediately."""
        # Request worker to stop any current speech
        self._task_queue.put({'type': 'stop_now'})
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices on the system.
        
        Returns:
            List of voice information dictionaries
        """
        # Request voices from worker and wait for response
        resp_event = threading.Event()
        container: List = []
        self._task_queue.put({'type': 'get_voices', 'resp_event': resp_event, 'container': container})
        resp_event.wait(timeout=3)
        return container[0] if container else []
    
    def cleanup(self):
        """Clean up TTS engine resources."""
        # Signal worker to stop and wait
        self._stop_event.set()
        self._task_queue.put({'type': 'shutdown'})
        self._worker.join(timeout=3)
        print("[TTS] Resources cleaned up.")

    def _worker_loop(self):
        """Worker thread that owns the pyttsx3 engine and processes tasks."""
        engine = None
        try:
            while not self._stop_event.is_set():
                try:
                    task = self._task_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                ttype = task.get('type')

                if ttype == 'setup':
                    try:
                        engine = pyttsx3.init()
                        # configure voice selection
                        voices = engine.getProperty('voices')
                        selected_voice = None
                        for voice in voices:
                            vname = getattr(voice, 'name', '').lower()
                            if self.voice_gender == 'female' and ('female' in vname or 'zira' in vname or 'hazel' in vname):
                                selected_voice = voice.id
                                break
                            if self.voice_gender == 'male' and ('male' in vname or 'david' in vname or 'mark' in vname):
                                selected_voice = voice.id
                                break
                        if not selected_voice and voices:
                            selected_voice = voices[0].id
                        if selected_voice:
                            engine.setProperty('voice', selected_voice)
                        engine.setProperty('rate', task.get('rate', self.rate))
                        engine.setProperty('volume', task.get('volume', self.volume))
                        print('[TTS] Text-to-Speech engine initialized (worker).')
                    except Exception as e:
                        print(f'[TTS] ERROR initializing engine in worker: {e}')
                    finally:
                        self._ready_event.set()

                elif ttype == 'speak':
                    text = task.get('text', '')
                    done_event = task.get('done_event')
                    if engine and text:
                        try:
                            # runAndWait is blocking inside worker thread
                            engine.say(text)
                            engine.runAndWait()
                        except Exception as e:
                            print(f'[TTS] ERROR during speech: {e}')
                    if done_event:
                        done_event.set()

                elif ttype == 'set_rate' and engine:
                    try:
                        engine.setProperty('rate', task.get('rate', self.rate))
                    except Exception:
                        pass

                elif ttype == 'set_volume' and engine:
                    try:
                        engine.setProperty('volume', task.get('volume', self.volume))
                    except Exception:
                        pass

                elif ttype == 'get_voices' and engine:
                    resp_event = task.get('resp_event')
                    container = task.get('container')
                    voices = engine.getProperty('voices')
                    voice_list = []
                    for voice in voices:
                        voice_info = {
                            'id': voice.id,
                            'name': getattr(voice, 'name', ''),
                            'languages': getattr(voice, 'languages', []),
                            'gender': getattr(voice, 'gender', 'unknown')
                        }
                        voice_list.append(voice_info)
                    if container is not None:
                        container.append(voice_list)
                    if resp_event:
                        resp_event.set()

                elif ttype == 'stop_now' and engine:
                    try:
                        engine.stop()
                    except Exception:
                        pass

                elif ttype == 'shutdown':
                    break

                try:
                    self._task_queue.task_done()
                except Exception:
                    pass

        finally:
            try:
                if engine:
                    try:
                        engine.stop()
                    except Exception:
                        pass
            except Exception:
                pass


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