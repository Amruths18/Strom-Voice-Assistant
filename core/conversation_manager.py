"""
Conversation Manager for Strom AI Assistant
Manages conversation history and context
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class ConversationManager:
    """
    Manages conversation context and history.
    """
    
    def __init__(self, history_file: str = "data/conversation_history.json", max_history: int = 50):
        """Initialize conversation manager."""
        self.history_file = history_file
        self.max_history = max_history
        self.conversation_history = []
        self.current_context = {}
        self.last_intent = None
        self.last_entities = {}
        
        self._load_history()
        print("[ConvManager] Initialized")
    
    def _load_history(self):
        """Load conversation history."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.conversation_history = json.load(f)
            except:
                self.conversation_history = []
    
    def _save_history(self):
        """Save conversation history."""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            with open(self.history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            print(f"[ConvManager] Save error: {str(e)}")
    
    def add_exchange(self, user_input: str, intent: str, entities: Dict, response: str):
        """Add conversation exchange."""
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'intent': intent,
            'entities': entities,
            'response': response
        }
        
        self.conversation_history.append(exchange)
        self.last_intent = intent
        self.last_entities = entities
        self._update_context(intent, entities)
        self._save_history()
    
    def _update_context(self, intent: str, entities: Dict):
        """Update context."""
        if intent in ['open_app', 'close_app']:
            self.current_context['last_app'] = entities.get('app_name')
        elif intent in ['send_whatsapp', 'send_email']:
            self.current_context['last_recipient'] = entities.get('recipient')
    
    def get_context(self, key: str) -> Optional[any]:
        """Get context value."""
        return self.current_context.get(key)
    
    def resolve_pronoun_reference(self, text: str) -> str:
        """Resolve pronouns."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['it', 'that']):
            if 'last_app' in self.current_context:
                text = text.replace('it', self.current_context['last_app'])
                text = text.replace('that', self.current_context['last_app'])
        
        return text
    
    def clear_context(self):
        """Clear context."""
        self.current_context = {}
        self.last_intent = None
        self.last_entities = {}