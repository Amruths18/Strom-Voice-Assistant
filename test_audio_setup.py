"""
Strom Audio Diagnostic Tool
Run this before starting Strom
"""

import sys
import os

print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        STROM AI ASSISTANT - AUDIO DIAGNOSTIC TOOL          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

# Check Python
print("1️⃣  Checking Python...")
if sys.version_info < (3, 8):
    print("   ❌ Python 3.8+ required")
    sys.exit(1)
print(f"   ✅ Python {sys.version.split()[0]}")

# Request microphone permission
def request_microphone_permission():
    """Request microphone permission on Windows."""
    try:
        # Load user32.dll
        user32 = ctypes.WinDLL('user32', use_last_error=True)

        # Define the message box function
        MessageBox = user32.MessageBoxW
        MessageBox.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
        MessageBox.restype = ctypes.c_int

        # Show permission request dialog
        result = MessageBox(
            None,
            "This application needs microphone access to test audio devices.\n\n"
            "Please grant microphone permission in the next dialog or Windows Settings.",
            "Microphone Permission Required",
            0x40 | 0x1  # MB_ICONINFORMATION | MB_OKCANCEL
        )

        if result == 1:  # IDOK
            print("   ✅ Microphone permission requested")
        else:
            print("   ⚠️  Microphone permission request cancelled")
    except Exception as e:
        print(f"   ⚠️  Could not request microphone permission: {str(e)}")

print("\n6️⃣  Requesting microphone permission...")
request_microphone_permission()

# Check packages
print("\n2️⃣  Checking dependencies...")
required = ['vosk', 'pyaudio', 'pyttsx3', 'numpy', 'yaml', 'requests', 'psutil']
missing = []

for pkg in required:
    try:
        __import__(pkg)
        print(f"   ✅ {pkg}")
    except ImportError:
        print(f"   ❌ {pkg}")
        missing.append(pkg)

if missing:
    print(f"\n   Install: pip install {' '.join(missing)}")
    sys.exit(1)

# Check Vosk model
print("\n3️⃣  Checking Vosk model...")
if os.path.exists('model') and os.path.isdir('model'):
    dirs = ['am', 'conf', 'graph']
    if all(os.path.exists(os.path.join('model', d)) for d in dirs):
        print("   ✅ Model found and valid")
    else:
        print("   ⚠️  Model incomplete")
else:
    print("   ❌ Model not found")
    print("\n   Download: https://alphacephei.com/vosk/models")
    print("   Get: vosk-model-small-en-us-0.15")
    sys.exit(1)

# Test audio
print("\n4️⃣  Testing audio devices...")
from utils.audio_utils import AudioUtils

utils = AudioUtils()
devices = utils.list_audio_devices()

if not devices:
    print("   ❌ No microphone found")
    utils.cleanup()
    sys.exit(1)

# Test microphone
print("\n5️⃣  Testing microphone (3 seconds)...")
print("   Speak into your microphone!\n")
result = utils.test_microphone(duration=3)

utils.cleanup()

# Final result
print("\n" + "="*60)
if result:
    print("  ✅ ALL TESTS PASSED!")
    print("\n  Run Strom: python main.py")
else:
    print("  ❌ MICROPHONE TEST FAILED")
    print("\n  Check microphone connection and permissions")
print("="*60 + "\n")