"""
Strom AI Assistant - Main Entry Point
Voice-based AI assistant with offline-first design
"""

import sys
import os
import yaml
import signal
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hotword_listener import HotwordListener
from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.nlp_engine import NLPEngine
from core.command_router import CommandRouter
from core.conversation_manager import ConversationManager

from modules.system_control import SystemControl
from modules.task_manager import TaskManager
from modules.messaging import Messaging
from modules.general_knowledge import GeneralKnowledge

from utils.security import Security
from utils.validator import Validator


class StromAssistant:
    """
    Main Strom AI Assistant class.
    """
    
    def __init__(self):
        """Initialize Strom."""
        print("\n" + "="*60)
        print("  STROM AI ASSISTANT")
        print("  Voice-Powered Desktop Assistant")
        print("="*60 + "\n")
        
        # GUI Callbacks
        self.on_status_change = None
        self.on_user_input = None
        self.on_assistant_response = None
        
        self.config = self._load_config()
        self.api_config = self._load_api_config()
        
        print("[Strom] Initializing components...")
        self._initialize_core()
        self._initialize_modules()
        
        self.router.register_routes()
        
        self.is_active = False
        self.is_running = True
        
        print("\n[Strom] ✅ Ready (Text Mode)!\n")
        
        self.is_voice_available = False
        self.is_voice_loading = False

        # Voice self-introduction if available
        # Voice introduction will happen after voice load
        # if self.is_voice_available:
        #      self._voice_introduction()
        # else:
        #      print("\n[Strom] ⚠️ Voice components unavailable. Running in Text-Only mode.\n")

        # signal.signal(signal.SIGINT, self._signal_handler) # Moved to run()
    
    def _load_config(self) -> dict:
        """Load configuration."""
        try:
            with open('config/settings.yaml', 'r') as f:
                return yaml.safe_load(f)
        except:
            return self._default_config()
    
    def _load_api_config(self) -> dict:
        """Load API config."""
        try:
            with open('config/api.yaml', 'r') as f:
                return yaml.safe_load(f)
        except:
            return {}
    
    def _default_config(self) -> dict:
        """Default config."""
        return {
            'voice': {
                'wake_word': 'hey strom',
                'stop_word': 'stop strom',
                'tts': {'rate': 150, 'volume': 0.9, 'voice_gender': 'female'},
                'stt': {'offline_model_path': 'model', 'sample_rate': 16000, 'use_online': False}
            },
            'behavior': {
                'greeting_message': "Hello! I'm Strom. How can I help?",
                'error_message': "Sorry, I encountered an error."
            }
        }
    
    def _initialize_core(self):
        """Initialize core components (Text only first)."""
        self._initialize_text_core()
        
    def _initialize_text_core(self):
        """Initialize text-based components."""
        print("[Strom] Initializing text components...")
        self.nlp = NLPEngine()
        self.router = CommandRouter()
        self.conv_manager = ConversationManager()
        self.security = Security()
        self.validator = Validator()
        # Placeholders for voice
        self.hotword = None
        self.stt = None
        self.tts = None

    def initialize_voice_core(self):
        """Initialize voice components (Heavy operation)."""
        if self.is_voice_available or self.is_voice_loading:
            return

        self.is_voice_loading = True
        print("[Strom] Initializing voice components (Lazy Load)...")
        
        voice = self.config.get('voice', {})
        tts_cfg = voice.get('tts', {})
        stt_cfg = voice.get('stt', {})
        
        try:
            # Load TTS first as it is lighter
            self.tts = TextToSpeech(
                rate=tts_cfg.get('rate', 150),
                volume=tts_cfg.get('volume', 0.9),
                voice_gender=tts_cfg.get('voice_gender', 'female')
            )
            
            # Load STT / Hotword (Heavy)
            self.hotword = HotwordListener(
                wake_word=voice.get('wake_word', 'hey strom'),
                stop_word=voice.get('stop_word', 'stop strom'),
                model_path=stt_cfg.get('offline_model_path', 'model')
            )
            
            self.stt = SpeechToText(
                model_path=stt_cfg.get('offline_model_path', 'model'),
                use_online=stt_cfg.get('use_online', False),
                silence_threshold=stt_cfg.get('silence_threshold', 300),
                silence_duration=stt_cfg.get('silence_duration', 1.5)
            )
            
            self.is_voice_available = True
            print("[Strom] ✅ Voice components loaded!")
            self._voice_introduction()
            
        except Exception as e:
            print(f"[Strom] ⚠️ Voice initialization failed: {str(e)}")
            print("[Strom] Continuing in text-only mode.")
            self.is_voice_available = False
            # Clean up partials
            if self.hotword: self.hotword = None
            if self.stt: self.stt = None
            # Keep TTS if it loaded? Maybe, but simpler to disable all.
            # self.tts = None 
            
        finally:
            self.is_voice_loading = False
    
    def _initialize_modules(self):
        """Initialize modules."""
        self.router.register_module('system_control', SystemControl())
        self.router.register_module('task_manager', TaskManager())
        
        email_cfg = self.api_config.get('email', {})
        self.router.register_module('messaging', Messaging(
            email_address=email_cfg.get('email_address'),
            email_password=email_cfg.get('email_password')
        ))
        
        self.router.register_module('general_knowledge', GeneralKnowledge(
            weather_api_key=self.api_config.get('weather', {}).get('api_key'),
            news_api_key=self.api_config.get('news', {}).get('api_key')
        ))

    def _voice_introduction(self):
        """Voice self-introduction."""
        intro_text = "Hello! Im Strom, your smart voice assistant. Speak your command, and lets get started."
        print(f"\n🎤 {intro_text}")
        if self.tts:
            self.tts.speak(intro_text)

    def _signal_handler(self, signum, frame):
        """Handle shutdown."""
        print("\n\n[Strom] Shutting down...")
        self.is_running = False
        self.cleanup()
        sys.exit(0)
    
    def speak(self, text: str):
        """Make Strom speak."""
        print(f"\n🗣️  Strom: {text}\n")
        if self.on_assistant_response:
            self.on_assistant_response(text)
        if self.tts:
            self.tts.speak(text)
    
    def listen(self) -> str:
        """Listen for command with enhanced error handling."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.stt:
                    return ""
                    
                text = self.stt.listen_and_transcribe(duration=self.config.get('voice', {}).get('stt', {}).get('recording_duration', 10))
                if text:
                    print(f"👤 You: {text}")
                    if self.on_user_input:
                        self.on_user_input(text)
                    return text
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        self.speak("I didn't catch that. Could you please repeat?")
                        print(f"[Strom] Retry {retry_count}/{max_retries}")
                    else:
                        self.speak("I'm having trouble hearing you. Let's try again later.")
                        return ""
                        
            except Exception as e:
                print(f"[Strom] Listen error (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(0.5)  # Brief pause before retry
        
        return ""
    
    def process(self, user_input: str) -> str:
        """Process command."""
        try:
            user_input = self.conv_manager.resolve_pronoun_reference(user_input)
            user_input = self.security.sanitize_input(user_input)
            
            intent, entities = self.nlp.process(user_input)
            
            is_valid, msg = self.security.validate_command(intent, entities)
            if not is_valid:
                return msg
            
            response = self.router.route(intent, entities)
            
            self.security.log_command(intent, entities)
            self.conv_manager.add_exchange(user_input, intent, entities, response)
            
            return response
            
        except Exception as e:
            print(f"[Strom] Process error: {str(e)}")
            return self.config.get('behavior', {}).get('error_message', "Error occurred.")
    
    def run(self):
        """Main loop."""
        print("\n" + "="*60)
        print("  STROM IS LISTENING")
        print("="*60)
        print(f"  Say '{self.config['voice']['wake_word']}' to activate")
        print(f"  Say '{self.config['voice']['stop_word']}' to deactivate")
        print("  Press Ctrl+C to exit")
        print("="*60 + "\n")
        
        if not self.is_voice_available:
            print("[Strom] Voice mode unavailable. Waiting for GUI/API commands...")
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                # Allow graceful shutdown on Ctrl+C without additional handling
                pass
            return

        self.hotword.start_listening()
        
        try:
            while self.is_running:
                detection = self.hotword.detect_hotword()
                
                if detection == 'wake' and not self.is_active:
                    self.is_active = True
                    self.hotword.is_active = True
                    
                    greeting = self.config.get('behavior', {}).get('greeting_message', "Hello! I'm Strom. How can I help?")
                    greeting = self.config.get('behavior', {}).get('greeting_message', "Hello! I'm Strom. How can I help?")
                    if self.on_status_change:
                        self.on_status_change("Listening...")
                    self.speak(greeting)
                    
                    # Listen for command with timeout
                    command_start = time.time()
                    user_input = ""
                    
                    while not user_input and (time.time() - command_start) < 30:  # 30 second timeout
                        user_input = self.listen()
                        if not user_input:
                            time.sleep(0.1)  # Brief pause
                    
                    if user_input:
                        response = self.process(user_input)
                        self.speak(response)
                    
                    self.is_active = False
                    self.hotword.is_active = False
                    
                    if user_input:
                        standby_msg = "How else can I help?"
                    else:
                        standby_msg = "Standing by."
                    
                    print(f"\n💤 {standby_msg} Say '{self.config['voice']['wake_word']}' to wake...\n")
                    if self.on_status_change:
                        self.on_status_change("Standing by")
                
                elif detection == 'stop' and self.is_active:
                    self.is_active = False
                    self.hotword.is_active = False
                    self.speak("Okay, standing by.")
                    print(f"\n💤 Say '{self.config['voice']['wake_word']}' to wake...\n")
                    if self.on_status_change:
                        self.on_status_change("Standing by")
                
                # Small delay to prevent CPU hogging
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\n[Strom] Interrupted")
        except Exception as e:
            print(f"\n\n[Strom] Fatal error: {str(e)}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("\n[Strom] Cleaning up...")
        
        try:
            if self.hotword: self.hotword.cleanup()
            if self.stt: self.stt.cleanup()
            if self.tts: self.tts.cleanup()
            print("[Strom] ✅ Cleanup complete")
        except:
            pass
        
        print("\n" + "="*60)
        print("  STROM SHUTDOWN COMPLETE")
        print("  Thank you!")
        print("="*60 + "\n")


def check_dependencies():
    """Check dependencies."""
    required = ['vosk', 'pyaudio', 'pyttsx3', 'requests', 'psutil', 'yaml', 'numpy']
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print("\n❌ Missing packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print(f"\nInstall: pip install {' '.join(missing)}\n")
        return False
    
    return True


def check_vosk_model():
    """Check Vosk model."""
    if not os.path.exists('model'):
        print("\n❌ Vosk model not found!")
        print("\nDownload from: https://alphacephei.com/vosk/models")
        print("Recommended: vosk-model-small-en-us-0.15")
        print("Extract to 'model' folder\n")
        return False
    
    return True


def main():
    """Main entry point."""
    # Remove strict dependency checks that kill the app
    # if not check_dependencies():
    #     sys.exit(1)
    
    # if not check_vosk_model():
    #     sys.exit(1)
    
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    try:
        strom = StromAssistant()
        strom.run()
    except Exception as e:
        print(f"\n❌ Fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()