"""
Enhanced Audio Utilities for Strom AI Assistant
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
        """List audio input devices with enhanced detection."""
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

                    # Test device accessibility
                    is_working = self._test_device_quick(i)

                    device = {
                        'index': i,
                        'name': device_info.get('name'),
                        'channels': device_info.get('maxInputChannels'),
                        'sample_rate': int(device_info.get('defaultSampleRate')),
                        'is_default': is_default,
                        'is_working': is_working
                    }
                    devices.append(device)

                    status = " ⭐ DEFAULT" if is_default else ""
                    status += " ✅ WORKING" if is_working else " ⚠️  ISSUE"
                    print(f"  [{i}] {device_info.get('name')}{status}")
            except Exception as e:
                print(f"  [{i}] Error checking device: {str(e)}")

        print(f"{'='*60}\n")

        if not devices:
            print("  ❌ No input devices found!")
            return []

        # Filter working devices
        working_devices = [d for d in devices if d['is_working']]
        if working_devices:
            print(f"  ✅ Found {len(working_devices)} working input device(s)")
        else:
            print("  ⚠️  No working input devices found!")

        return devices
    
    def _test_device_quick(self, device_index: int) -> bool:
        """Quick test if device is accessible."""
        try:
            # Try to open and close stream quickly
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            stream.close()
            return True
        except:
            return False

    def get_default_input_device(self) -> Optional[int]:
        """Get default input device."""
        try:
            device = self.audio.get_default_input_device_info()
            return device['index']
        except:
            return None
    
    def test_microphone(self, duration: int = 3, device_index: Optional[int] = None) -> bool:
        """Test microphone."""
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
            
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            frames = []
            num_chunks = int(self.sample_rate / 1024 * duration)
            
            print("[AudioUtils] Level: ", end="", flush=True)
            
            for i in range(num_chunks):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
                
                audio_data = np.frombuffer(data, dtype=np.int16)
                level = np.sqrt(np.mean(audio_data**2))
                bars = int(level / 100)
                
                print(f"\r[AudioUtils] Level: {'█' * min(bars, 40)} {int(level):4d}", end="", flush=True)
            
            print()
            
            stream.stop_stream()
            stream.close()
            
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            max_amp = np.max(np.abs(audio_data))
            avg_amp = np.mean(np.abs(audio_data))
            
            print(f"\n[AudioUtils] Results:")
            print(f"  Max: {max_amp}")
            print(f"  Avg: {int(avg_amp)}")
            
            if max_amp > 1000:
                print(f"  Status: ✅ Working well!")
                return True
            elif max_amp > 100:
                print(f"  Status: ⚠️ Working but weak")
                print(f"  Tip: Speak louder or closer")
                return True
            else:
                print(f"  Status: ❌ Too weak or not working")
                return False
                
        except Exception as e:
            print(f"\n[AudioUtils] ❌ Test failed: {str(e)}")
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
        utils.test_microphone(duration=3, device_index=default)
    
    utils.cleanup()