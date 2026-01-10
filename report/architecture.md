# System Architecture

## Strom AI Assistant - Architecture Documentation

### 1. Overview

Strom follows a **layered, modular architecture** that separates concerns and promotes maintainability, scalability, and testability. The system is designed with an **offline-first** philosophy, ensuring core functionality works without internet connectivity while seamlessly integrating online services when available.

---

### 2. Architectural Layers
```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                  │
│                  (Voice Input/Output)                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      CORE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Hotword    │  │   Speech to  │  │   Text to    │  │
│  │   Listener   │  │     Text     │  │    Speech    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │     NLP      │  │   Command    │  │Conversation  │  │
│  │   Engine     │  │   Router     │  │  Manager     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    MODULE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   System     │  │     Task     │  │  Messaging   │  │
│  │   Control    │  │   Manager    │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐                                       │
│  │   General    │                                       │
│  │  Knowledge   │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   UTILITY LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Audio     │  │   Security   │  │  Validator   │  │
│  │    Utils     │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                            │
│     JSON Files, Configuration, Logs, Cache               │
└─────────────────────────────────────────────────────────┘
```

---

### 3. Component Details

#### 3.1 Core Layer Components

**Hotword Listener**
- Purpose: Continuously monitors audio input for wake/stop words
- Technology: Vosk offline speech recognition
- Functionality: Activates/deactivates the assistant without manual interaction

**Speech-to-Text (STT)**
- Purpose: Converts voice commands to text
- Technology: Vosk (offline) with Whisper API fallback (online)
- Functionality: Automatic mode selection based on network availability

**Text-to-Speech (TTS)**
- Purpose: Converts assistant responses to voice output
- Technology: pyttsx3 (offline)
- Functionality: Configurable voice, rate, and volume

**NLP Engine**
- Purpose: Extracts intent and entities from user commands
- Technology: Rule-based pattern matching with keyword extraction
- Functionality: Maps natural language to actionable intents

**Command Router**
- Purpose: Routes intents to appropriate module handlers
- Technology: Intent-to-module mapping system
- Functionality: Centralized dispatch mechanism for all commands

**Conversation Manager**
- Purpose: Maintains conversation context and history
- Technology: JSON-based persistent storage
- Functionality: Enables follow-up questions and context-aware responses

#### 3.2 Module Layer Components

**System Control**
- Capabilities: Shutdown, restart, lock, application management, volume/brightness control
- Platform Support: Windows, macOS, Linux
- Security: Command validation and confirmation for dangerous operations

**Task Manager**
- Capabilities: Alarms, reminders, to-do lists, timers
- Storage: Persistent JSON files
- Background Processing: Timer threads and reminder checkers

**Messaging**
- Capabilities: WhatsApp messages (via web), email sending
- Requirements: Online connectivity, API credentials
- Contact Management: Name-to-contact mapping

**General Knowledge**
- Capabilities: Weather, news, time/date, web search, Wikipedia
- APIs: OpenWeatherMap, News API, Wikipedia
- Fallback: Offline responses when services unavailable

#### 3.3 Utility Layer Components

**Audio Utils**
- Audio device management and configuration
- Noise reduction and audio enhancement
- Microphone testing and level monitoring

**Security**
- Command validation and sanitization
- Protection against dangerous operations
- Command logging for audit trails

**Validator**
- Input validation (time, date, duration, etc.)
- Data type checking and conversion
- Relative time expression parsing

---

### 4. Data Flow
```
1. User speaks wake word
   ↓
2. Hotword Listener detects activation
   ↓
3. TTS announces readiness
   ↓
4. STT captures and transcribes command
   ↓
5. NLP Engine extracts intent and entities
   ↓
6. Security validates command
   ↓
7. Command Router dispatches to module
   ↓
8. Module executes action
   ↓
9. Response sent to TTS
   ↓
10. TTS speaks response to user
    ↓
11. Conversation Manager saves exchange
```

---

### 5. Offline-First Design

**Offline Capabilities:**
- Wake word detection (Vosk)
- Speech recognition (Vosk)
- Text-to-speech (pyttsx3)
- System control commands
- Task management (local storage)
- Basic question answering

**Online Enhancements:**
- Improved STT accuracy (Whisper API)
- Weather information
- News updates
- Web search
- Email sending
- Wikipedia queries

**Network Detection:**
- Automatic connectivity checking
- Graceful degradation to offline mode
- User notification of limited functionality

---

### 6. Configuration Management

**settings.yaml**: Core system settings
- Voice parameters (wake word, TTS settings)
- Module enable/disable flags
- Behavior configurations
- Logging preferences

**api.yaml**: External service credentials
- API keys (OpenAI, Weather, News)
- Email SMTP configuration
- Contact mappings
- Network timeout settings

---

### 7. Security Architecture

**Multi-Layer Protection:**
1. Input sanitization (remove dangerous characters)
2. Command validation (check for dangerous operations)
3. Confirmation requirements (for critical actions)
4. Path protection (prevent access to system directories)
5. Audit logging (track all command executions)

---

### 8. Extensibility

The modular architecture allows easy extension:

**Adding New Modules:**
1. Create module class in `modules/`
2. Implement required methods
3. Register with Command Router
4. Add intent patterns to NLP Engine
5. Update route map in Command Router

**Adding New Features:**
1. Extend existing modules
2. Add new intent keywords
3. Update configuration files
4. Maintain backward compatibility

---

### 9. Technology Stack

**Core Technologies:**
- Python 3.8+
- Vosk (offline STT)
- pyttsx3 (offline TTS)
- PyAudio (audio I/O)

**Libraries:**
- requests (HTTP)
- psutil (system info)
- wikipedia (knowledge base)
- pyyaml (configuration)
- numpy (audio processing)

**Optional APIs:**
- OpenAI Whisper (online STT)
- OpenWeatherMap (weather)
- News API (news)
- SMTP (email)

---

### 10. Performance Considerations

**Optimization Strategies:**
- Asynchronous audio processing
- Background reminder checking
- Lazy module initialization
- Caching of frequently accessed data
- Minimal memory footprint for continuous operation

**Resource Management:**
- Proper cleanup of audio streams
- Thread management for timers
- File handle management for logs
- Configuration caching

---

This architecture ensures Strom is robust, maintainable, and easily extensible while providing a seamless user experience in both online and offline scenarios.