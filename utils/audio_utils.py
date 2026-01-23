"""
Enhanced Audio Utilities for Strom AI Assistant
Fixed NaN handling and better error checking
"""

import pyaudio
import numpy as np
from typing import Optional, List, Dict
import time


class AudioUtils:
    """
    Audio utilities with device management.
    """
    
    def __init__(self, sample_rate: int = 16000):
        """Initialize audio utils."""
        self.sample_rate = sample_rate
        self.audio = pyaudio.PyAudio()
        print("[AudioUtils] Initialized")
    
    def list_audio_devices(self) -> List[Dict]:
        """List audio input devices."""
        devices = []
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        print(f"\n{'='*60}")
        print("  AUDIO INPUT DEVICES")
        print(f"{'='*60}")
        
        for i in range(num_devices):
            try:
                device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
                
                if device_info.get('maxInputChannels') > 0:
                    is_default = False
                    try:
                        default = self.audio.get_default_input_device_info()
                        is_default = (i == default['index'])
                    except:
                        pass
                    
                    device = {
                        'index': i,
                        'name': device_info.get('name'),
                        'channels': device_info.get('maxInputChannels'),
                        'sample_rate': int(device_info.get('defaultSampleRate')),
                        'is_default': is_default
                    }
                    devices.append(device)
                    
                    marker = " ⭐ DEFAULT" if is_default else ""
                    print(f"  [{i}] {device_info.get('name')}{marker}")
            except:
                pass
        
        print(f"{'='*60}\n")
        
        if not devices:
            print("  ❌ No input devices found!")
        
        return devices
    
    def get_default_input_device(self) -> Optional[int]:
        """Get default input device."""
        try:
            device = self.audio.get_default_input_device_info()
            return device['index']
        except:
            return None
    
    def calculate_audio_level(self, data: bytes) -> int:
        """
        Calculate audio level with NaN protection.
        Returns level from 0-100.
        """
        try:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Check if data is valid
            if len(audio_data) == 0:
                return 0
            
            # Remove any NaN or inf values
            audio_data = audio_data[np.isfinite(audio_data)]
            
            if len(audio_data) == 0:
                return 0
            
            # Calculate RMS with safety checks
            squared = audio_data.astype(np.float64) ** 2
            mean_squared = np.mean(squared)
            
            # Check for negative or NaN values
            if mean_squared < 0 or np.isnan(mean_squared) or np.isinf(mean_squared):
                return 0
            
            rms = np.sqrt(mean_squared)
            
            # Check final result
            if np.isnan(rms) or np.isinf(rms):
                return 0
            
            # Normalize to 0-100 range
            # Typical speech is around 1000-10000 RMS
            level = min(100, int((rms / 3000) * 100))
            
            return max(0, level)
            
        except Exception as e:
            print(f"[AudioUtils] Level calc error: {str(e)}")
            return 0
    
    def test_microphone(self, duration: int = 3, device_index: Optional[int] = None) -> bool:
        """Test microphone with improved error handling."""
        if device_index is None:
            device_index = self.get_default_input_device()
        
        if device_index is None:
            print("[AudioUtils] ❌ No device for testing")
            return False
        
        try:
            device = self.audio.get_device_info_by_index(device_index)
            print(f"\n[AudioUtils] Testing: {device['name']}")
            print(f"[AudioUtils] Duration: {duration}s")
            print(f"[AudioUtils] Speak into microphone...\n")
            
            # Open stream with error handling
            try:
                stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024
                )
            except Exception as e:
                print(f"[AudioUtils] ❌ Failed to open stream: {str(e)}")
                print("\nSOLUTIONS:")
                print("  1. Close other apps using microphone")
                print("  2. Reconnect microphone")
                print("  3. Check system permissions")
                return False
            
            frames = []
            num_chunks = int(self.sample_rate / 1024 * duration)
            max_level = 0
            total_level = 0
            valid_chunks = 0
            
            print("[AudioUtils] Level: ", end="", flush=True)
            
            for i in range(num_chunks):
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    frames.append(data)
                    
                    # Calculate level with NaN protection
                    level = self.calculate_audio_level(data)
                    
                    if level > 0:
                        max_level = max(max_level, level)
                        total_level += level
                        valid_chunks += 1
                    
                    # Visual feedback
                    bars = min(level // 2, 40)  # Scale to fit in 40 chars
                    print(f"\r[AudioUtils] Level: {'█' * bars}{' ' * (40 - bars)} {level:3d}%", end="", flush=True)
                    
                except Exception as e:
                    print(f"\n[AudioUtils] Read error: {str(e)}")
                    continue
            
            print()  # New line
            
            stream.stop_stream()
            stream.close()
            
            # Calculate statistics
            avg_level = total_level // valid_chunks if valid_chunks > 0 else 0
            
            # Also check raw audio amplitude
            try:
                all_audio = np.frombuffer(b''.join(frames), dtype=np.int16)
                all_audio = all_audio[np.isfinite(all_audio)]
                
                if len(all_audio) > 0:
                    max_amplitude = np.max(np.abs(all_audio))
                    avg_amplitude = int(np.mean(np.abs(all_audio)))
                else:
                    max_amplitude = 0
                    avg_amplitude = 0
            except:
                max_amplitude = 0
                avg_amplitude = 0
            
            print(f"\n[AudioUtils] Test Results:")
            print(f"  Max Level: {max_level}%")
            print(f"  Avg Level: {avg_level}%")
            print(f"  Max Amplitude: {max_amplitude}")
            print(f"  Avg Amplitude: {avg_amplitude}")
            print(f"  Valid Chunks: {valid_chunks}/{num_chunks}")
            
            # Determine if microphone is working
            if max_amplitude > 1000 or max_level > 20:
                print(f"  Status: ✅ Microphone is working!")
                return True
            elif max_amplitude > 100 or max_level > 5:
                print(f"  Status: ⚠️ Microphone working but signal is weak")
                print(f"  Suggestions:")
                print(f"    - Speak louder")
                print(f"    - Move closer to microphone")
                print(f"    - Increase microphone volume in system settings")
                return True
            else:
                print(f"  Status: ❌ Microphone signal too weak or not working")
                print(f"\n  TROUBLESHOOTING:")
                print(f"    1. Check if microphone is muted in system settings")
                print(f"    2. Increase microphone volume/boost")
                print(f"    3. Try a different microphone")
                print(f"    4. Test microphone in other apps (e.g., Voice Recorder)")
                print(f"    5. Update audio drivers")
                return False
                
        except Exception as e:
            print(f"\n[AudioUtils] ❌ Test failed: {str(e)}")
            print(f"\n  TROUBLESHOOTING:")
            print(f"    1. Check microphone connection")
            print(f"    2. Check system permissions for microphone access")
            print(f"    3. Close other applications using the microphone")
            print(f"    4. Try a different microphone or USB port")
            return False
    
    def cleanup(self):
        """Clean up."""
        if self.audio:
            self.audio.terminate()


if __name__ == "__main__":
    print("="*60)
    print("  AUDIO DIAGNOSTICS")
    print("="*60)
    
    utils = AudioUtils()
    devices = utils.list_audio_devices()
    
    if devices:
        default = utils.get_default_input_device()
        print(f"Testing device index: {default}")
        utils.test_microphone(duration=3, device_index=default)
    else:
        print("\n❌ No audio devices available!")
    
    utils.cleanup()