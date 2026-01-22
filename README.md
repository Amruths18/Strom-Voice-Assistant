<h1> Working On Implement Conditions </h1>
# Strom AI Assistant 🎤

Voice-powered desktop AI assistant with offline-first design.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Vosk Model
- Visit: https://alphacephei.com/vosk/models
- Download: vosk-model-small-en-us-0.15
- Extract to project root as `model/` folder

### 3. Run Diagnostic
```bash
python test_audio_setup.py
```

### 4. Start Strom
```bash
python main.py
```

Say **"Hey Strom"** to activate!

## Voice Commands

- "Shutdown the computer"
- "Open Chrome"
- "Set an alarm for 7 AM"
- "What time is it?"
- "Create a todo: finish report"
- "Search for Python tutorials"

## Troubleshooting

### No microphone detected
- Check connection
- Check system permissions
- Close other apps using mic

### Poor recognition
- Speak clearly
- Reduce background noise
- Use better microphone

### Model not found
- Download and extract model
- Place in project root as `model/`

## Features

✅ Offline wake word detection  
✅ Voice recognition (offline)  
✅ Natural voice output  
✅ System control  
✅ Task management  
✅ Information services  

## License

Open source - use freely
