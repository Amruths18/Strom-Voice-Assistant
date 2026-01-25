# Module Description

## Strom AI Assistant - Detailed Module Documentation

### Core Modules

---

#### 1. Hotword Listener (`core/hotword_listener.py`)

**Purpose**: Continuously listens for wake and stop words to activate/deactivate the assistant.

**Key Features:**
- Offline wake word detection using Vosk
- Low-latency audio stream processing
- Configurable wake/stop phrases
- Callback system for activation events
- Thread-safe audio queue

**Technical Details:**
- Sample Rate: 16000 Hz
- Audio Format: 16-bit PCM
- Processing: Real-time streaming recognition
- Default Wake Word: "Hello Strom"
- Default Stop Word: "Stop Strom"

**Methods:**
- `start_listening()`: Initiates audio capture
- `detect_hotword()`: Processes audio for wake/stop words
- `listen_loop()`: Main continuous listening loop
- `cleanup()`: Releases audio resources

**Usage Example:**
```python
listener = HotwordListener(wake_word="hello strom", stop_word="stop strom")
listener.listen_loop(on_wake=activate_callback, on_stop=deactivate_callback)
```

---

#### 2. Speech-to-Text (`core/speech_to_text.py`)

**Purpose**: Converts spoken commands to text using offline/online methods.

**Key Features:**
- Offline recognition with Vosk
- Online recognition with Whisper API (optional)
- Automatic network detection
- Graceful fallback mechanism
- Configurable recording duration

**Technical Details:**
- Primary Engine: Vosk (offline)
- Fallback Engine: OpenAI Whisper (online)
- Audio Format: WAV, 16-bit, mono
- Maximum Duration: Configurable (default 5 seconds)

**Methods:**
- `listen_and_transcribe()`: Main method for voice capture
- `record_audio()`: Records audio from microphone
- `transcribe_offline()`: Uses Vosk for transcription
- `transcribe_online()`: Uses Whisper API for transcription
- `is_online()`: Checks internet connectivity

**Hybrid Operation:**
```
┌─────────────┐
│ User Speaks │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Record Audio    │
└──────┬──────────┘
       │
       ▼
┌──────────────────────┐      Yes    ┌──────────────┐
│ Online Available?    │──────────────▶│ Whisper API  │
└──────┬───────────────┘             └──────┬───────┘
       │ No                                  │
       ▼                                     │
┌──────────────┐                            │
│ Vosk Offline │                            │
└──────┬───────┘                            │
       │                                     │
       └──────────────┬──────────────────────┘
                      ▼
              ┌───────────────┐
              │ Transcribed   │
              │ Text Output   │
              └───────────────┘
```

---

#### 3. Text-to-Speech (`core/text_to_speech.py`)

**Purpose**: Converts text responses to natural-sounding voice output.

**Key Features:**
- Offline voice synthesis with pyttsx3
- Configurable voice parameters
- Male/female voice selection
- Adjustable speech rate and volume
- Blocking and non-blocking modes

**Technical Details:**
- Engine: pyttsx3 (platform-native)
- Default Rate: 150 WPM
- Default Volume: 0.9 (0.0-1.0 scale)
- Voice Gender: Configurable

**Methods:**
- `speak()`: Convert text to speech
- `set_rate()`: Adjust speech speed
- `set_volume()`: Adjust volume level
- `stop()`: Interrupt current speech
- `get_available_voices()`: List system voices

**Configuration:**
```yaml
tts:
  rate: 150          # Words per minute
  volume: 0.9        # 0.0 to 1.0
  voice_gender: "female"
```

---

#### 4. NLP Engine (`core/nlp_engine.py`)

**Purpose**: Extracts intent and entities from natural language commands.

**Key Features:**
- Rule-based pattern matching
- Keyword extraction
- Entity recognition
- Context-aware processing
- Offline operation

**Supported Intents:**
- System Control: shutdown, restart, lock, open_app, close_app, volume, brightness
- Task Management: set_alarm, set_reminder, create_todo, list_todos, set_timer
- Messaging: send_whatsapp, send_email
- Knowledge: weather, time, date, news, search, wikipedia
- Conversation: greeting, thanks, goodbye, help

**Entity Extraction:**
- Application names
- Contact names/emails
- Time values (hour, minute)
- Durations (seconds, minutes, hours)
- Task descriptions
- Search queries
- Volume/brightness levels

**Methods:**
- `process()`: Main processing method (returns intent and entities)
- `extract_intent()`: Identifies command intent
- `extract_entities()`: Extracts relevant data based on intent

**Example:**
```python
nlp = NLPEngine()
intent, entities = nlp.process("set an alarm for 7:30 AM")
# Returns: ('set_alarm', {'hour': 7, 'minute': 30})
```

---

#### 5. Command Router (`core/command_router.py`)

**Purpose**: Routes processed intents to appropriate module handlers.

**Key Features:**
- Centralized command dispatch
- Module registration system
- Intent-to-method mapping
- Error handling and fallbacks
- Internal conversation handling

**Architecture:**
```
User Command
     │
     ▼
┌──────────────┐
│ NLP Engine   │
│ (Intent +    │
│  Entities)   │
└──────┬───────┘
       │
       ▼
┌───────────────────┐
│ Command Router    │
│ - Route Map       │
│ - Module Registry │
└──────┬────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌──────────┐   ┌───────────┐  ┌──────────┐  ┌──────────┐
│ System   │   │   Task    │  │Messaging │  │ General  │
│ Control  │   │  Manager  │  │          │  │Knowledge │
└──────────┘   └───────────┘  └──────────┘  └──────────┘
```

**Methods:**
- `register_module()`: Register feature modules
- `register_routes()`: Map intents to handlers
- `route()`: Dispatch command to module
- `get_available_modules()`: List registered modules

---

#### 6. Conversation Manager (`core/conversation_manager.py`)

**Purpose**: Maintains conversation context and history for multi-turn interactions.

**Key Features:**
- Persistent conversation storage
- Context retention
- Pronoun resolution
- Follow-up question detection
- History summarization

**Data Storage:**
```json
{
  "timestamp": "2025-01-08T10:30:00",
  "user_input": "open chrome",
  "intent": "open_app",
  "entities": {"app_name": "chrome"},
  "response": "Opening Chrome..."
}
```

**Context Management:**
- Stores last app opened/closed
- Remembers last recipient for messages
- Retains recent search queries
- Tracks last alarm/reminder time

**Methods:**
- `add_exchange()`: Record conversation exchange
- `get_context()`: Retrieve context value
- `resolve_pronoun_reference()`: Handle pronouns (it, that, him, her)
- `is_follow_up_question()`: Detect follow-ups
- `get_recent_history()`: Retrieve recent exchanges
- `get_summary()`: Generate session summary

---

### Feature Modules

---

#### 7. System Control (`modules/system_control.py`)

**Purpose**: Manages system-level operations and application control.

**Capabilities:**

**Power Management:**
- Shutdown computer
- Restart computer
- Lock screen
- Sleep/hibernate

**Application Management:**
- Open applications
- Close applications
- Support for common apps (Chrome, Notepad, Calculator, etc.)

**System Settings:**
- Volume control (set, increase, decrease, mute)
- Brightness control (set, increase, decrease)

**Platform Support:**
- Windows (primary)
- macOS (Darwin)
- Linux

**Methods:**
- `shutdown()`: Power off system
- `restart()`: Reboot system
- `lock_screen()`: Lock user session
- `sleep()`: Suspend system
- `open_application()`: Launch app
- `close_application()`: Terminate app
- `control_volume()`: Adjust system volume
- `control_brightness()`: Adjust screen brightness

**Security:**
- Command validation
- Dangerous operation warnings
- Confirmation requirements

---

#### 8. Task Manager (`modules/task_manager.py`)

**Purpose**: Manages personal tasks, reminders, alarms, and timers.

**Features:**

**To-Do Tasks:**
- Create tasks
- List pending tasks
- Mark as complete
- Persistent storage

**Alarms:**
- Set time-based alarms
- 24-hour format support
- Auto-adjustment for next day

**Reminders:**
- Text-based reminders
- Time-specific notifications
- Background checking

**Timers:**
- Countdown timers
- Background thread execution
- Duration in hours/minutes/seconds

**Data Storage:**
```json
// user_tasks.json
{
  "id": 1,
  "description": "Buy groceries",
  "created_at": "2025-01-08T10:00:00",
  "completed": false
}

// reminders.json
{
  "id": 1,
  "type": "reminder",
  "time": "2025-01-08T15:00:00",
  "message": "Team meeting",
  "triggered": false
}
```

**Methods:**
- `create_todo()`: Add new task
- `list_todos()`: Show pending tasks
- `set_alarm()`: Schedule alarm
- `set_reminder()`: Create reminder
- `set_timer()`: Start countdown timer

**Background Processing:**
- Reminder checker runs every 30 seconds
- Timer threads execute independently
- Automatic notification triggering

---

#### 9. Messaging (`modules/messaging.py`)

**Purpose**: Handles communication through WhatsApp and email.

**WhatsApp Integration:**
- Opens WhatsApp Web with pre-filled message
- Contact name resolution
- Direct phone number support
- Browser-based interaction

**Email Support:**
- SMTP-based email sending
- Gmail app password support
- Configurable SMTP servers
- Contact management

**Configuration:**
```yaml
email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  email_address: "your@email.com"
  email_password: "app_password"
  use_tls: true
```

**Methods:**
- `send_whatsapp()`: Send WhatsApp message
- `send_email()`: Send email message
- `get_contact_email()`: Lookup email by name
- `get_contact_phone()`: Lookup phone by name

**Requirements:**
- Internet connectivity
- Valid SMTP credentials for email
- WhatsApp Web account for messaging

---

#### 10. General Knowledge (`modules/general_knowledge.py`)

**Purpose**: Provides information and answers to general queries.

**Capabilities:**

**Time & Date:**
- Current time
- Current date
- Timezone support

**Weather:**
- Current weather conditions
- Temperature
- Location-based forecasts
- OpenWeatherMap API integration

**News:**
- Top headlines
- Category filtering
- News API integration
- Configurable sources

**Web Search:**
- Opens browser with search query
- Google search integration

**Wikipedia:**
- Article summaries
- Disambiguation handling
- 3-sentence summaries

**General Queries:**
- Offline fallback responses
- Suggestion to search online
- Context-aware answers

**Methods:**
- `get_time()`: Return current time
- `get_date()`: Return current date
- `get_weather()`: Fetch weather info
- `get_news()`: Retrieve headlines
- `web_search()`: Perform web search
- `wikipedia_search()`: Query Wikipedia
- `answer_query()`: Handle general questions

**API Configuration:**
```yaml
weather:
  api_key: "your_openweathermap_key"
  units: "metric"

news:
  api_key: "your_newsapi_key"
  country: "us"
  category: "general"
```

---

### Utility Modules

---

#### 11. Audio Utils (`utils/audio_utils.py`)

**Purpose**: Audio processing utilities and device management.

**Features:**
- Device listing and selection
- Microphone testing
- Noise reduction
- Audio normalization
- Volume level monitoring
- WAV file operations

**Methods:**
- `list_audio_devices()`: Show available devices
- `test_microphone()`: Verify mic functionality
- `reduce_noise()`: Apply noise gate
- `normalize_audio()`: Adjust audio levels
- `get_audio_level()`: Monitor input volume
- `save_audio()`: Export to WAV file

---

#### 12. Security (`utils/security.py`)

**Purpose**: Security validation and protection mechanisms.

**Features:**
- Command validation
- Input sanitization
- Protected path enforcement
- Dangerous command detection
- Audit logging
- Email/phone validation

**Methods:**
- `validate_command()`: Check command safety
- `sanitize_input()`: Remove dangerous characters
- `require_confirmation()`: Check if confirmation needed
- `validate_email()`: Email format check
- `validate_phone()`: Phone number validation
- `log_command()`: Audit trail logging

---

#### 13. Validator (`utils/validator.py`)

**Purpose**: Input validation and data type checking.

**Features:**
- Time validation (hour, minute)
- Date parsing (multiple formats)
- Duration validation
- Volume level checking
- Application name validation
- Message content validation
- Relative time parsing ("in 5 minutes", "tomorrow")
- URL validation

**Methods:**
- `validate_time()`: Check hour/minute values
- `validate_date()`: Parse date strings
- `validate_duration()`: Check duration range
- `validate_volume_level()`: Verify 0-100 range
- `validate_app_name()`: Check app name safety
- `validate_message()`: Check message content
- `parse_relative_time()`: Handle relative expressions
- `is_valid_url()`: URL format checking

---

Each module is designed to be:
- **Independent**: Can be tested and developed separately
- **Reusable**: Clear interfaces for easy integration
- **Maintainable**: Well-documented with clear responsibilities
- **Extensible**: Easy to add new features without breaking existing functionality