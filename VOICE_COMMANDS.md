# Strom AI Assistant - Voice Commands Guide

## 🚀 Quick Start
1. Run: `python main.py`
2. Say: **"Hello Strom"** to wake up the assistant
3. Give voice commands naturally
4. Say: **"Stop Strom"** to deactivate

## 🎯 System Control Commands

### Power Management
- **"Shutdown the computer"** - Shuts down your PC
- **"Restart the computer"** - Restarts your PC
- **"Lock the screen"** - Locks your computer
- **"Put computer to sleep"** - Puts system to sleep

### Application Control
- **"Open Notepad"** - Opens Notepad
- **"Open Calculator"** - Opens Calculator
- **"Open Chrome"** - Opens Google Chrome
- **"Open Word"** - Opens Microsoft Word
- **"Open Excel"** - Opens Microsoft Excel
- **"Close Chrome"** - Closes Google Chrome

### System Information
- **"Take a screenshot"** - Captures screen (requires PIL)
- **"What's the system status"** - Shows CPU, memory, battery info
- **"Set volume to 50 percent"** - Adjusts system volume
- **"Mute the volume"** - Mutes system audio

## 📋 Task Management Commands

### Todo Lists
- **"Add task buy groceries"** - Adds a new task
- **"List my tasks"** - Shows all pending tasks
- **"Complete task number 1"** - Marks task as done
- **"Delete task number 3"** - Removes a task

### Time Management
- **"Set alarm for 7 AM"** - Sets wake-up alarm
- **"Remind me to drink water in 1 hour"** - Sets reminder
- **"Set timer for 10 minutes"** - Starts countdown timer

## 💬 Communication Commands

### Messaging
- **"Send WhatsApp to John saying hello"** - Opens WhatsApp
- **"Email to boss saying meeting at 3pm"** - Opens email client

## 🧠 Information Commands

### Time & Date
- **"What time is it"** - Tells current time
- **"What date is today"** - Tells current date

### Search & Information
- **"Search for Python tutorials"** - Opens browser with search
- **"Wikipedia Python programming"** - Opens Wikipedia page
- **"Get weather"** - Shows weather (requires API key)
- **"Show news"** - Shows news headlines (requires API key)

## 🎤 Voice Interaction Tips

### Best Practices
- Speak clearly and at normal volume
- Wait for Strom to finish responding before new commands
- Use natural language - "Hello Strom, open Chrome" works great
- Say "Stop Strom" anytime to cancel current interaction

### Wake Words
- **"Hello Strom"** - Primary wake word
- **"Hi Strom"** - Alternative wake word
- **"Stop Strom"** - Deactivation word

## ⚙️ Configuration

### API Keys (Optional)
Edit `config/api.yaml` for enhanced features:
```yaml
weather:
  api_key: "your_openweather_api_key"
news:
  api_key: "your_newsapi_key"
email:
  email_address: "your_email@gmail.com"
  email_password: "your_app_password"
```

### Voice Settings
Edit `config/settings.yaml` to customize:
- Wake/stop words
- TTS voice and speed
- STT sensitivity
- Recording duration

## 🔧 Troubleshooting

### Common Issues
- **"No speech detected"** - Speak louder or closer to microphone
- **"Failed to open application"** - Check if app is installed
- **"API not configured"** - Add API keys to config/api.yaml
- **"Microphone not working"** - Run `python test_audio_setup.py`

### Performance Tips
- Close other applications using microphone
- Use external microphone for better quality
- Ensure good lighting for better recognition
- Update Vosk models for improved accuracy

## 📊 System Requirements

- Python 3.8+
- Working microphone
- Internet connection (for online features)
- Vosk speech recognition models
- Windows/Linux/macOS

## 🎯 Example Conversation

```
You: "Hello Strom"
Strom: "Hello! I'm Strom. How can I help?"

You: "Open Chrome"
Strom: "Opening Chrome..."

You: "Add task finish project report"
Strom: "Added task: finish project report"

You: "Set timer for 5 minutes"
Strom: "Timer set for 5 minutes."

You: "What time is it"
Strom: "It's 2:30 PM."

You: "Stop Strom"
Strom: "Okay, standing by."
```

## 🚀 Advanced Features

### Batch Commands
Strom can handle complex commands:
- **"Open Chrome and set timer for 30 minutes"** - Multiple actions
- **"Add task buy milk, bread, and eggs"** - Complex task creation

### Smart Recognition
- Fuzzy wake word matching
- Context-aware responses
- Error recovery and retries
- Silence detection for natural pauses

---

**Ready to automate? Run `python main.py` and say "Hello Strom"!** 🎤✨