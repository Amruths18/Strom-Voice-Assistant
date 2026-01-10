"""
Natural Language Processing Engine for Strom AI Assistant
Extracts intent and entities from user commands using rule-based pattern matching.
Offline-first design with keyword matching and simple NLP techniques.
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class NLPEngine:
    """
    Processes natural language input to extract intent and entities.
    Uses rule-based pattern matching for offline operation.
    """
    
    def __init__(self):
        """Initialize NLP engine with intent patterns and keywords."""
        
        # Intent patterns with keywords
        self.intent_patterns = {
            # System Control
            'shutdown': ['shutdown', 'shut down', 'power off', 'turn off computer'],
            'restart': ['restart', 'reboot', 'reset computer'],
            'lock': ['lock', 'lock screen', 'lock computer'],
            'sleep': ['sleep', 'hibernate', 'suspend'],
            'open_app': ['open', 'launch', 'start', 'run'],
            'close_app': ['close', 'quit', 'exit', 'kill'],
            'volume': ['volume', 'sound', 'mute', 'unmute'],
            'brightness': ['brightness', 'screen brightness', 'dim', 'brighten'],
            
            # Task Management
            'set_alarm': ['alarm', 'wake me', 'set alarm'],
            'set_reminder': ['remind', 'reminder', 'remember'],
            'create_todo': ['todo', 'to do', 'task', 'add task'],
            'list_todos': ['list tasks', 'show tasks', 'what tasks', 'my tasks'],
            'set_timer': ['timer', 'set timer', 'countdown'],
            
            # Messaging
            'send_whatsapp': ['whatsapp', 'send whatsapp', 'message on whatsapp'],
            'send_email': ['email', 'send email', 'mail'],
            
            # General Knowledge
            'weather': ['weather', 'temperature', 'forecast'],
            'time': ['time', 'what time', 'current time'],
            'date': ['date', 'what date', 'today'],
            'news': ['news', 'headlines', 'latest news'],
            'search': ['search', 'look up', 'find', 'google'],
            'wikipedia': ['wikipedia', 'wiki', 'tell me about'],
            
            # Conversation
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'thanks': ['thank', 'thanks', 'thank you'],
            'goodbye': ['bye', 'goodbye', 'see you', 'exit'],
            'help': ['help', 'what can you do', 'commands', 'capabilities']
        }
        
        # Application name mappings
        self.app_aliases = {
            'chrome': 'google chrome',
            'browser': 'google chrome',
            'notepad': 'notepad',
            'calculator': 'calculator',
            'calc': 'calculator',
            'word': 'microsoft word',
            'excel': 'microsoft excel',
            'powerpoint': 'microsoft powerpoint',
            'explorer': 'file explorer',
            'files': 'file explorer',
            'code': 'visual studio code',
            'vscode': 'visual studio code',
            'spotify': 'spotify',
            'music': 'spotify'
        }
        
        print("[NLP] Engine initialized with intent patterns.")
    
    def extract_intent(self, text: str) -> str:
        """
        Extract primary intent from user text.
        
        Args:
            text: User's spoken command
            
        Returns:
            Detected intent string
        """
        text_lower = text.lower().strip()
        
        # Check each intent pattern
        for intent, keywords in self.intent_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    print(f"[NLP] Intent detected: {intent}")
                    return intent
        
        # Default to search if no specific intent matched
        print("[NLP] Intent detected: general_query")
        return 'general_query'
    
    def extract_entities(self, text: str, intent: str) -> Dict:
        """
        Extract relevant entities based on detected intent.
        
        Args:
            text: User's spoken command
            intent: Detected intent
            
        Returns:
            Dictionary of extracted entities
        """
        text_lower = text.lower().strip()
        entities = {}
        
        # Application name extraction
        if intent in ['open_app', 'close_app']:
            app_name = self._extract_app_name(text_lower)
            entities['app_name'] = app_name
        
        # Contact/recipient extraction
        if intent in ['send_whatsapp', 'send_email']:
            recipient = self._extract_recipient(text_lower)
            message = self._extract_message(text_lower)
            entities['recipient'] = recipient
            entities['message'] = message
        
        # Time extraction
        if intent in ['set_alarm', 'set_reminder', 'set_timer']:
            time_info = self._extract_time(text_lower)
            entities.update(time_info)
        
        # Task/reminder text extraction
        if intent in ['create_todo', 'set_reminder']:
            task_text = self._extract_task_text(text_lower, intent)
            entities['task'] = task_text
        
        # Search query extraction
        if intent in ['search', 'wikipedia']:
            query = self._extract_search_query(text_lower, intent)
            entities['query'] = query
        
        # Volume/brightness level extraction
        if intent in ['volume', 'brightness']:
            level = self._extract_level(text_lower)
            entities['level'] = level
            entities['action'] = self._extract_action(text_lower)
        
        print(f"[NLP] Entities extracted: {entities}")
        return entities
    
    def _extract_app_name(self, text: str) -> str:
        """Extract application name from text."""
        for alias, full_name in self.app_aliases.items():
            if alias in text:
                return full_name
        
        # Try to extract word after 'open' or 'close'
        patterns = [r'open\s+(\w+)', r'launch\s+(\w+)', r'close\s+(\w+)', r'start\s+(\w+)']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_recipient(self, text: str) -> str:
        """Extract recipient name from message command."""
        patterns = [
            r'(?:to|message)\s+(\w+(?:\s+\w+)?)',
            r'(?:whatsapp|email)\s+(?:to\s+)?(\w+(?:\s+\w+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_message(self, text: str) -> str:
        """Extract message content from message command."""
        patterns = [
            r'(?:saying|message|text)\s+(.+)',
            r'(?:that|tell them)\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_time(self, text: str) -> Dict:
        """Extract time information from text."""
        time_info = {}
        
        # Extract hour and minute
        time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?'
        match = re.search(time_pattern, text)
        
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            period = match.group(3)
            
            # Convert to 24-hour format
            if period and 'pm' in period.lower() and hour != 12:
                hour += 12
            elif period and 'am' in period.lower() and hour == 12:
                hour = 0
            
            time_info['hour'] = hour
            time_info['minute'] = minute
        
        # Extract duration (for timers)
        duration_patterns = [
            r'(\d+)\s*hour(?:s)?',
            r'(\d+)\s*minute(?:s)?',
            r'(\d+)\s*second(?:s)?'
        ]
        
        for i, pattern in enumerate(duration_patterns):
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                if i == 0:  # hours
                    time_info['duration_seconds'] = value * 3600
                elif i == 1:  # minutes
                    time_info['duration_seconds'] = value * 60
                else:  # seconds
                    time_info['duration_seconds'] = value
        
        return time_info
    
    def _extract_task_text(self, text: str, intent: str) -> str:
        """Extract task description from text."""
        # Remove command keywords
        remove_words = ['todo', 'to do', 'task', 'remind', 'reminder', 'create', 'add', 'set']
        
        clean_text = text
        for word in remove_words:
            clean_text = clean_text.replace(word, '')
        
        # Remove time expressions
        clean_text = re.sub(r'at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?', '', clean_text)
        clean_text = re.sub(r'(?:in|after)\s+\d+\s+(?:hour|minute|second)s?', '', clean_text)
        
        return clean_text.strip()
    
    def _extract_search_query(self, text: str, intent: str) -> str:
        """Extract search query from text."""
        # Remove command keywords
        remove_patterns = [
            r'search\s+(?:for\s+)?',
            r'look\s+up\s+',
            r'find\s+(?:me\s+)?',
            r'google\s+',
            r'wikipedia\s+',
            r'tell\s+me\s+about\s+'
        ]
        
        clean_text = text
        for pattern in remove_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        return clean_text.strip()
    
    def _extract_level(self, text: str) -> Optional[int]:
        """Extract volume or brightness level (0-100)."""
        # Look for percentage
        match = re.search(r'(\d+)\s*(?:percent|%)', text)
        if match:
            return int(match.group(1))
        
        # Look for keywords
        if any(word in text for word in ['max', 'maximum', 'full', 'hundred']):
            return 100
        if any(word in text for word in ['min', 'minimum', 'zero']):
            return 0
        if any(word in text for word in ['half', 'fifty']):
            return 50
        
        return None
    
    def _extract_action(self, text: str) -> str:
        """Extract action type (increase, decrease, set, mute)."""
        if any(word in text for word in ['up', 'increase', 'raise', 'higher', 'louder', 'brighter']):
            return 'increase'
        if any(word in text for word in ['down', 'decrease', 'lower', 'dimmer', 'quieter']):
            return 'decrease'
        if 'mute' in text or 'silent' in text:
            return 'mute'
        if 'unmute' in text:
            return 'unmute'
        return 'set'
    
    def process(self, text: str) -> Tuple[str, Dict]:
        """
        Main processing method: extract intent and entities.
        
        Args:
            text: User's spoken command
            
        Returns:
            Tuple of (intent, entities)
        """
        if not text or not text.strip():
            return 'unknown', {}
        
        intent = self.extract_intent(text)
        entities = self.extract_entities(text, intent)
        
        return intent, entities


# Test function
def _test_nlp_engine():
    """Test the NLP engine with sample commands."""
    
    print("=== Strom NLP Engine Test ===\n")
    
    nlp = NLPEngine()
    
    test_commands = [
        "open chrome",
        "shutdown the computer",
        "set an alarm for 7:30 AM",
        "remind me to buy groceries at 5 PM",
        "send whatsapp to John saying hello",
        "what's the weather today",
        "increase volume to 80 percent",
        "create a todo to finish the report",
        "search for python tutorials"
    ]
    
    for command in test_commands:
        print(f"Command: \"{command}\"")
        intent, entities = nlp.process(command)
        print(f"  Intent: {intent}")
        print(f"  Entities: {entities}\n")


if __name__ == "__main__":
    _test_nlp_engine()