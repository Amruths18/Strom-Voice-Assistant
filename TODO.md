# Task: Replace Vosk with Hugging Face Whisper for Speech-to-Text

## Steps to Complete:
- [ ] Install required dependencies: transformers, torch, torchaudio
- [ ] Update core/speech_to_text.py to use Whisper pipeline instead of Vosk
- [ ] Test the updated speech-to-text functionality
- [ ] Remove old Vosk model files from model/ directory
- [ ] Update requirements or setup files if needed

## Notes:
- Using openai/whisper-large-v3 as the best available model on Hugging Face
- Keeping online fallback option intact
- Removing Vosk imports and related code
