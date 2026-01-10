"""
Audio Utilities for Strom AI Assistant
Provides audio processing utilities including noise reduction,
microphone configuration, and audio quality enhancement.
"""

import pyaudio
import wave
import numpy as np
from typing import Optional, Tuple


class AudioUtils:
    """
    Utility functions for audio processing and configuration.
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize audio utilities.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.audio = pyaudio.PyAudio()
        print("[AudioUtils] Audio utilities initialized.")
    
    def list_audio_devices(self) -> list:
        """
        List all available audio input devices.
        
        Returns:
            List of device information dictionaries
        """
        devices = []
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        for i in range(0, num_devices):
            device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
            
            # Only include input devices
            if device_info.get('maxInputChannels') > 0:
                devices.append({
                    'index': i,
                    'name': device_info.get('name'),
                    'channels': device_info.get('maxInputChannels'),
                    'sample_rate': int(device_info.get('defaultSampleRate'))
                })
        
        return devices
    
    def get_default_input_device(self) -> Optional[int]:
        """
        Get default audio input device index.
        
        Returns:
            Device index or None
        """
        try:
            default_device = self.audio.get_default_input_device_info()
            return default_device['index']
        except:
            return None
    
    def test_microphone(self, duration: int = 3) -> bool:
        """
        Test microphone by recording for a few seconds.
        
        Args:
            duration: Test recording duration in seconds
            
        Returns:
            True if microphone works, False otherwise
        """
        try:
            print(f"[AudioUtils] Testing microphone for {duration} seconds...")
            
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            for i in range(0, int(self.sample_rate / 1024 * duration)):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Check if audio was captured
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            max_amplitude = np.max(np.abs(audio_data))
            
            if max_amplitude > 100:  # Arbitrary threshold
                print("[AudioUtils] ✅ Microphone is working!")
                return True
            else:
                print("[AudioUtils] ⚠️ Microphone is too quiet or not working.")
                return False
                
        except Exception as e:
            print(f"[AudioUtils] ❌ Microphone test failed: {str(e)}")
            return False
    
    def reduce_noise(self, audio_data: np.ndarray, noise_reduction_strength: float = 0.3) -> np.ndarray:
        """
        Apply basic noise reduction to audio data.
        
        Args:
            audio_data: Audio data as numpy array
            noise_reduction_strength: Strength of noise reduction (0.0 to 1.0)
            
        Returns:
            Noise-reduced audio data
        """
        # Simple noise gate implementation
        threshold = np.max(np.abs(audio_data)) * noise_reduction_strength
        audio_data[np.abs(audio_data) < threshold] = 0
        
        return audio_data
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio volume.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Normalized audio data
        """
        max_val = np.max(np.abs(audio_data))
        
        if max_val > 0:
            audio_data = audio_data / max_val * 32767 * 0.9  # Leave some headroom
        
        return audio_data.astype(np.int16)
    
    def save_audio(self, audio_data: bytes, filename: str, channels: int = 1):
        """
        Save audio data to WAV file.
        
        Args:
            audio_data: Raw audio bytes
            filename: Output filename
            channels: Number of audio channels
        """
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
            wf.close()
            print(f"[AudioUtils] Audio saved to {filename}")
        except Exception as e:
            print(f"[AudioUtils] Error saving audio: {str(e)}")
    
    def get_audio_level(self, duration: float = 0.5) -> int:
        """
        Get current microphone audio level.
        
        Args:
            duration: Sampling duration in seconds
            
        Returns:
            Audio level (0-100)
        """
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            num_frames = int(self.sample_rate / 1024 * duration)
            
            for i in range(num_frames):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Calculate RMS level
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Normalize to 0-100
            level = int(min(100, (rms / 3000) * 100))
            
            return level
            
        except Exception as e:
            print(f"[AudioUtils] Error getting audio level: {str(e)}")
            return 0
    
    def cleanup(self):
        """Clean up audio resources."""
        if self.audio:
            self.audio.terminate()
        print("[AudioUtils] Resources cleaned up.")


# Test function
def _test_audio_utils():
    """Test audio utilities."""
    
    print("=== Strom Audio Utils Test ===\n")
    
    audio_utils = AudioUtils()
    
    # List devices
    print("Available Audio Devices:")
    devices = audio_utils.list_audio_devices()
    for device in devices:
        print(f"  [{device['index']}] {device['name']}")
    print()
    
    # Get default device
    default = audio_utils.get_default_input_device()
    print(f"Default Input Device: {default}\n")
    
    # Test microphone
    print("Testing microphone...")
    audio_utils.test_microphone(duration=3)
    print()
    
    # Get audio level
    print("Getting current audio level...")
    level = audio_utils.get_audio_level()
    print(f"Audio Level: {level}%\n")
    
    audio_utils.cleanup()


if __name__ == "__main__":
    _test_audio_utils()