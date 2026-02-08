"""
Enhanced Audio Test for Strom AI Assistant
Test the improved listening and voice interaction
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hotword_listener import HotwordListener
from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech

def test_hotword():
    """Test hotword detection."""
    print("\n" + "="*50)
    print("  HOTWORD DETECTION TEST")
    print("="*50)

    listener = HotwordListener(wake_word="hello strom", stop_word="stop strom")

    try:
        listener.start_listening()
        print("Say 'hello strom' or 'stop strom' to test...")
        print("Press Ctrl+C to stop test\n")

        start_time = time.time()
        detections = []

        while time.time() - start_time < 10:  # 10 second test
            detection = listener.detect_hotword()
            if detection:
                detections.append(detection)
                print(f"✅ Detected: {detection}")
                if len(detections) >= 2:  # Stop after 2 detections
                    break
            time.sleep(0.01)

        if not detections:
            print("❌ No hotwords detected")
        else:
            print(f"✅ Detected {len(detections)} hotword(s)")

    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        listener.cleanup()

def test_stt():
    """Test speech-to-text."""
    print("\n" + "="*50)
    print("  SPEECH-TO-TEXT TEST")
    print("="*50)

    stt = SpeechToText(use_online=False, silence_threshold=300, silence_duration=1.5)

    try:
        print("Speak a short sentence (3-5 seconds)...")
        text = stt.listen_and_transcribe(duration=5)

        if text:
            print(f"✅ Recognized: '{text}'")
        else:
            print("❌ No speech recognized")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        stt.cleanup()

def test_tts():
    """Test text-to-speech."""
    print("\n" + "="*50)
    print("  TEXT-TO-SPEECH TEST")
    print("="*50)

    tts = TextToSpeech(rate=160, volume=0.8, voice_gender="female")

    try:
        test_text = "Hello! This is an enhanced voice test for Strom AI Assistant."
        print(f"Speaking: '{test_text}'")
        tts.speak(test_text)
        print("✅ TTS test completed")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        tts.cleanup()

def main():
    """Run all tests."""
    print("STROM ENHANCED AUDIO TEST SUITE")
    print("Testing improved listening and voice interaction\n")

    # Test TTS first (non-blocking)
    test_tts()

    # Test STT
    test_stt()

    # Test hotword
    test_hotword()

    print("\n" + "="*50)
    print("  TEST SUITE COMPLETED")
    print("="*50)

if __name__ == "__main__":
    main()