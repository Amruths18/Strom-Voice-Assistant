# Strom Setup Guide

## Step-by-Step Installation

### 1. Prerequisites
- Python 3.8+
- Microphone
- Speakers

### 2. Clone/Download
```bash
# Download and extract Strom files
cd Strom_AI_Assistant
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Vosk Model
```bash
# Visit: https://alphacephei.com/vosk/models
# Download: vosk-model-small-en-us-0.15.zip
# Extract to: Strom_AI_Assistant/model/
```

Your structure should be:
```
Strom_AI_Assistant/
├── model/
│   ├── am/
│   ├── conf/
│   ├── graph/
│   └── ivector/
├── main.py
└── ...
```

### 5. Test Setup
```bash
python test_audio_setup.py
```

Fix any issues reported.

### 6. Run Strom
```bash
python main.py
```

## Common Issues

### Issue: "No input devices"
**Solution:**
- Windows: Settings → Privacy → Microphone → Allow
- macOS: System Preferences → Security → Microphone
- Linux: `sudo usermod -a -G audio $USER`

### Issue: "Vosk model not found"
**Solution:**
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model
```

### Issue: "Microphone too quiet"
**Solution:**
- Increase mic volume in system settings
- Move closer to microphone
- Use external USB microphone

## Configuration

Edit `config/settings.yaml`:
```yaml
voice:
  wake_word: "hey strom"  # Change this
  tts:
    rate: 150  # Speech speed
    volume: 0.9  # Volume level
```

## Testing Individual Components
```bash
# Test microphone
python utils/audio_utils.py

# Test speech recognition
python core/speech_to_text.py

# Test text-to-speech
python core/text_to_speech.py
```

## Success!

When everything works:
1. Run `python main.py`
2. Wait for "STROM IS LISTENING"
3. Say "Hey Strom"
4. Speak your command
5. Strom will respond!