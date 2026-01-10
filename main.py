"""
Strom AI Assistant - Main Entry Point
A fully voice-based AI assistant that works offline-first with online capabilities.
Wake word: "Hey Strom" | Stop word: "Stop Strom"
"""

import sys
import os
import yaml
import signal
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import core modules
from core.hotword_listener import HotwordListener
from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.nlp_engine import NLPEngine
from core.command_router import CommandRouter
from core.conversation_manager import ConversationManager

# Import feature modules
from modules.system_control import SystemControl
from modules.task_manager import TaskManager
from modules.messaging import Messaging
from modules.general_knowledge import GeneralKnowledge

# Import utilities
from utils.security import Security
from utils.validator import Validator


class StromAssistant:
    """
    Main Strom AI Assistant class.
    Orchestrates all modules and handles the voice interaction loop.
    """
    
    def __init__(self):
        """Initialize Strom AI Assistant."""
        print("\n" + "="*60)
        print("  STROM AI ASSISTANT - Voice-Powered Desktop Assistant")
        print("="*60 + "\n")
        
        # Load configuration
        self.config = self._load_config()
        self.api_config = self._load_api_config()
        
        # Initialize core components
        print("[Strom] Initializing core components...")
        self._initialize_core_components()
        
        # Initialize feature modules
        print("[Strom] Initializing feature modules...")
        self._initialize_modules()
        
        # Register routes
        self.router.register_routes()
        
        # State management
        self.is_active = False
        self.is_running = True
        
        print("\n[Strom] ✅ Initialization complete!\n")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> dict:
        """Load settings configuration."""
        try:
            with open('config/settings.yaml', 'r') as f:
                config = yaml.safe_load(f)
            print("[Strom] Configuration loaded.")
            return config
        except Exception as e:
            print(f"[Strom] WARNING: Could not load config: {str(e)}")
            return self._get_default_config()
    
    def _load_api_config(self) -> dict:
        """Load API configuration."""
        try:
            with open('config/api.yaml', 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"[Strom] WARNING: Could not load API config: {str(e)}")
            return {}
    
    def _get_default_config(self) -> dict:
        """Get default configuration if file not found."""
        return {
            'voice': {
                'wake_word': 'hey strom',
                'stop_word': 'stop strom',
                'tts': {'rate': 150, 'volume': 0.9, 'voice_gender': 'female'},
                'stt': {'offline_model_path': 'model', 'sample_rate': 16000, 'use_online': True}
            },
            'behavior': {
                'greeting_message': "Hello! I'm Strom. How can I help you?",
                'error_message': "Sorry, I encountered an error."
            }
        }
    
    def _initialize_core_components(self):
        """Initialize core system components."""
        voice_config = self.config.get('voice', {})
        tts_config = voice_config.get('tts', {})
        stt_config = voice_config.get('stt', {})
        
        # Hotword listener
        self.hotword_listener = HotwordListener(
            wake_word=voice_config.get('wake_word', 'hey strom'),
            stop_word=voice_config.get('stop_word', 'stop strom'),
            model_path=stt_config.get('offline_model_path', 'model')
        )
        
        # Speech-to-Text
        whisper_key = self.api_config.get('openai', {}).get('api_key')
        self.stt = SpeechToText(
            model_path=stt_config.get('offline_model_path', 'model'),
            sample_rate=stt_config.get('sample_rate', 16000),
            whisper_api_key=whisper_key,
            use_online=stt_config.get('use_online', True)
        )
        
        # Text-to-Speech
        self.tts = TextToSpeech(
            rate=tts_config.get('rate', 150),
            volume=tts_config.get('volume', 0.9),
            voice_gender=tts_config.get('voice_gender', 'female')
        )
        
        # NLP Engine
        self.nlp = NLPEngine()
        
        # Command Router
        self.router = CommandRouter()
        
        # Conversation Manager
        self.conv_manager = ConversationManager()
        
        # Security & Validation
        self.security = Security()
        self.validator = Validator()
    
    def _initialize_modules(self):
        """Initialize feature modules and register with router."""
        # System Control
        system_control = SystemControl()
        self.router.register_module('system_control', system_control)
        
        # Task Manager
        task_manager = TaskManager()
        self.router.register_module('task_manager', task_manager)
        
        # Messaging
        email_config = self.api_config.get('email', {})
        messaging = Messaging(
            email_address=email_config.get('email_address'),
            email_password=email_config.get('email_password'),
            smtp_server=email_config.get('smtp_server', 'smtp.gmail.com'),
            smtp_port=email_config.get('smtp_port', 587)
        )
        self.router.register_module('messaging', messaging)
        
        # General Knowledge
        general_knowledge = GeneralKnowledge(
            weather_api_key=self.api_config.get('weather', {}).get('api_key'),
            news_api_key=self.api_config.get('news', {}).get('api_key')
        )
        self.router.register_module('general_knowledge', general_knowledge)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\n\n[Strom] Shutdown signal received. Cleaning up...")
        self.is_running = False
        self.cleanup()
        sys.exit(0)
    
    def speak(self, text: str):
        """Helper method to make Strom speak."""
        print(f"\n🗣️  Strom: {text}\n")
        self.tts.speak(text)
    
    def listen_for_command(self) -> Optional[str]:
        """Listen for user command and convert to text."""
        try:
            user_input = self.stt.listen_and_transcribe(duration=5)
            
            if user_input:
                print(f"👤 You: {user_input}")
                return user_input
            else:
                return None
                
        except Exception as e:
            print(f"[Strom] Error listening: {str(e)}")
            return None
    
    def process_command(self, user_input: str) -> str:
        """Process user command and generate response."""
        try:
            # Resolve references from context
            user_input = self.conv_manager.resolve_pronoun_reference(user_input)
            
            # Sanitize input
            user_input = self.security.sanitize_input(user_input)
            
            # Extract intent and entities
            intent, entities = self.nlp.process(user_input)
            
            # Validate command
            is_valid, validation_msg = self.security.validate_command(intent, entities)
            
            if not is_valid:
                return validation_msg
            
            # Route command to appropriate module
            response = self.router.route(intent, entities)
            
            # Log command for security audit
            self.security.log_command(intent, entities)
            
            # Save to conversation history
            self.conv_manager.add_exchange(user_input, intent, entities, response)
            
            return response
            
        except Exception as e:
            error_msg = self.config.get('behavior', {}).get('error_message', 
                                                           "Sorry, I encountered an error.")
            print(f"[Strom] Error processing command: {str(e)}")
            return error_msg
    
    def run(self):
        """Main execution loop."""
        print("\n" + "="*60)
        print("  STROM IS NOW LISTENING")
        print("="*60)
        print(f"  Say '{self.config['voice']['wake_word']}' to activate")
        print(f"  Say '{self.config['voice']['stop_word']}' to deactivate")
        print("  Press Ctrl+C to exit")
        print("="*60 + "\n")
        
        # Start hotword detection
        self.hotword_listener.start_listening()
        
        try:
            while self.is_running:
                # Check for wake/stop word
                detection = self.hotword_listener.detect_hotword()
                
                if detection == 'wake' and not self.is_active:
                    self.is_active = True
                    self.hotword_listener.is_active = True

                    greeting = self.config.get('behavior', {}).get('greeting_message',
                                                                   "Hello! How can I help you?")
                    self.speak(greeting)

                    # Stop hotword listening to avoid microphone conflict
                    self.hotword_listener.stop_listening()

                    # Listen and process command
                    user_input = self.listen_for_command()

                    if user_input:
                        response = self.process_command(user_input)
                        self.speak(response)

                    # Reset to inactive after command
                    self.is_active = False
                    self.hotword_listener.is_active = False

                    # Restart hotword listening
                    self.hotword_listener.start_listening()
                    print(f"\n💤 Say '{self.config['voice']['wake_word']}' to wake me up...\n")
                
                elif detection == 'stop' and self.is_active:
                    self.is_active = False
                    self.hotword_listener.is_active = False
                    self.speak("Okay, I'm standing by.")
        
        except KeyboardInterrupt:
            print("\n\n[Strom] Interrupted by user.")
        except Exception as e:
            print(f"\n\n[Strom] Fatal error: {str(e)}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exit."""
        print("\n[Strom] Cleaning up resources...")
        
        try:
            self.hotword_listener.cleanup()
            self.stt.cleanup()
            self.tts.cleanup()
            print("[Strom] ✅ Cleanup complete.")
        except Exception as e:
            print(f"[Strom] Error during cleanup: {str(e)}")
        
        print("\n" + "="*60)
        print("  STROM SHUTDOWN COMPLETE")
        print("  Thank you for using Strom AI Assistant!")
        print("="*60 + "\n")


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'vosk',
        'pyaudio',
        'pyttsx3',
        'requests',
        'psutil',
        'wikipedia',
        'yaml'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("\n❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall them using:")
        print(f"   pip install {' '.join(missing)}\n")
        return False
    
    return True


def check_vosk_model():
    """Check if Vosk model is downloaded."""
    if not os.path.exists('model'):
        print("\n❌ Vosk model not found!")
        print("\nPlease download a Vosk model:")
        print("   1. Visit: https://alphacephei.com/vosk/models")
        print("   2. Download: vosk-model-small-en-us-0.15")
        print("   3. Extract to project root as 'model' folder\n")
        return False
    
    return True


def main():
    """Main entry point."""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Vosk model
    if not check_vosk_model():
        sys.exit(1)
    
    # Create required directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    # Initialize and run Strom
    try:
        strom = StromAssistant()
        strom.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()