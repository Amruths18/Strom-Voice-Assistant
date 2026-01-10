"""
Conversation Manager for Strom AI Assistant
Manages conversation context, history, and follow-up question handling.
Enables natural multi-turn conversations with context retention.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class ConversationManager:
    """
    Manages conversation history and context for multi-turn interactions.
    Stores conversation data and maintains context across exchanges.
    """
    
    def __init__(self, history_file: str = "data/conversation_history.json", max_history: int = 50):
        """
        Initialize conversation manager.
        
        Args:
            history_file: Path to conversation history JSON file
            max_history: Maximum number of exchanges to keep in memory
        """
        self.history_file = history_file
        self.max_history = max_history
        self.conversation_history = []
        self.current_context = {}
        self.last_intent = None
        self.last_entities = {}
        
        # Load existing history
        self._load_history()
        print("[ConvManager] Conversation manager initialized.")
    
    def _load_history(self):
        """Load conversation history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.conversation_history = json.load(f)
                print(f"[ConvManager] Loaded {len(self.conversation_history)} previous exchanges.")
            except Exception as e:
                print(f"[ConvManager] Error loading history: {str(e)}")
                self.conversation_history = []
        else:
            print("[ConvManager] No previous history found.")
            self.conversation_history = []
    
    def _save_history(self):
        """Save conversation history to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # Keep only recent history
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
            
            with open(self.history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            print(f"[ConvManager] Error saving history: {str(e)}")
    
    def add_exchange(self, user_input: str, intent: str, entities: Dict, response: str):
        """
        Add a conversation exchange to history.
        
        Args:
            user_input: User's original command
            intent: Detected intent
            entities: Extracted entities
            response: Assistant's response
        """
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'intent': intent,
            'entities': entities,
            'response': response
        }
        
        self.conversation_history.append(exchange)
        
        # Update context
        self.last_intent = intent
        self.last_entities = entities
        self._update_context(intent, entities)
        
        # Save to file
        self._save_history()
        
        print(f"[ConvManager] Exchange recorded: {intent}")
    
    def _update_context(self, intent: str, entities: Dict):
        """Update current conversation context."""
        # Store relevant context based on intent
        if intent in ['open_app', 'close_app']:
            self.current_context['last_app'] = entities.get('app_name')
        
        elif intent in ['send_whatsapp', 'send_email']:
            self.current_context['last_recipient'] = entities.get('recipient')
            self.current_context['last_message'] = entities.get('message')
        
        elif intent in ['search', 'wikipedia']:
            self.current_context['last_query'] = entities.get('query')
        
        elif intent in ['set_alarm', 'set_reminder']:
            self.current_context['last_time'] = entities.get('hour')
    
    def get_context(self, key: str) -> Optional[any]:
        """
        Retrieve value from current context.
        
        Args:
            key: Context key to retrieve
            
        Returns:
            Context value or None
        """
        return self.current_context.get(key)
    
    def resolve_pronoun_reference(self, text: str) -> str:
        """
        Resolve pronouns and references to previous context.
        
        Args:
            text: User input text
            
        Returns:
            Text with resolved references
        """
        text_lower = text.lower()
        
        # Resolve "it", "that", "this"
        if any(word in text_lower for word in ['it', 'that', 'this']):
            if 'last_app' in self.current_context:
                text = text.replace('it', self.current_context['last_app'])
                text = text.replace('that', self.current_context['last_app'])
        
        # Resolve "him", "her", "them"
        if any(word in text_lower for word in ['him', 'her', 'them']):
            if 'last_recipient' in self.current_context:
                text = text.replace('him', self.current_context['last_recipient'])
                text = text.replace('her', self.current_context['last_recipient'])
                text = text.replace('them', self.current_context['last_recipient'])
        
        return text
    
    def is_follow_up_question(self, text: str) -> bool:
        """
        Determine if current input is a follow-up question.
        
        Args:
            text: User input text
            
        Returns:
            True if follow-up, False otherwise
        """
        follow_up_indicators = [
            'what about',
            'how about',
            'and',
            'also',
            'too',
            'as well',
            'more',
            'another',
            'again'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in follow_up_indicators)
    
    def get_recent_history(self, count: int = 5) -> List[Dict]:
        """
        Get recent conversation exchanges.
        
        Args:
            count: Number of recent exchanges to retrieve
            
        Returns:
            List of recent exchanges
        """
        return self.conversation_history[-count:] if self.conversation_history else []
    
    def clear_context(self):
        """Clear current conversation context."""
        self.current_context = {}
        self.last_intent = None
        self.last_entities = {}
        print("[ConvManager] Context cleared.")
    
    def clear_history(self):
        """Clear all conversation history."""
        self.conversation_history = []
        self.current_context = {}
        self.last_intent = None
        self.last_entities = {}
        self._save_history()
        print("[ConvManager] History cleared.")
    
    def get_summary(self) -> str:
        """
        Get summary of conversation session.
        
        Returns:
            Summary string
        """
        total_exchanges = len(self.conversation_history)
        
        if total_exchanges == 0:
            return "No conversation history yet."
        
        # Count intents
        intent_counts = {}
        for exchange in self.conversation_history:
            intent = exchange['intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        summary = f"Total exchanges: {total_exchanges}\n"
        summary += "Most common intents:\n"
        
        sorted_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)
        for intent, count in sorted_intents[:5]:
            summary += f"  - {intent}: {count}\n"
        
        return summary


# Test function
def _test_conversation_manager():
    """Test conversation manager functionality."""
    
    print("=== Strom Conversation Manager Test ===\n")
    
    # Initialize manager
    conv_manager = ConversationManager(history_file="data/test_conversation_history.json")
    
    # Simulate conversation
    exchanges = [
        ("open chrome", "open_app", {"app_name": "chrome"}, "Opening Chrome..."),
        ("close it", "close_app", {"app_name": "chrome"}, "Closing Chrome..."),
        ("send whatsapp to John", "send_whatsapp", {"recipient": "John", "message": "Hello"}, "Message sent."),
        ("what's the weather", "weather", {}, "It's sunny today.")
    ]
    
    for user_input, intent, entities, response in exchanges:
        print(f"User: {user_input}")
        print(f"Intent: {intent}")
        print(f"Response: {response}\n")
        
        conv_manager.add_exchange(user_input, intent, entities, response)
    
    # Test context retrieval
    print("Current context:", conv_manager.current_context)
    print("\nRecent history:")
    for exchange in conv_manager.get_recent_history(3):
        print(f"  - {exchange['user_input']} -> {exchange['response']}")
    
    # Test summary
    print("\n" + conv_manager.get_summary())


if __name__ == "__main__":
    _test_conversation_manager()