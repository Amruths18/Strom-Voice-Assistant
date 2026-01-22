"""
NLP Engine for Strom AI Assistant
Extracts intent and entities from commands
"""

import re
from typing import Dict, Tuple


class NLPEngine:
    """
    Processes natural language to extract intent and entities.
    """
    
    def __init__(self):
        """Initialize NLP engine."""
        
        self.intent_patterns = {
            'shutdown': ['shutdown', 'shut down', 'power off'],
            'restart': ['restart', 'reboot'],
            'lock': ['lock', 'lock screen'],
            'sleep': ['sleep', 'hibernate'],
            'screenshot': ['screenshot', 'screen capture', 'capture screen'],
            'system_info': ['system info', 'computer status', 'system status'],
            'open_app': ['open', 'launch', 'start', 'run'],
            'close_app': ['close', 'quit', 'exit'],
            'volume': ['volume', 'sound', 'mute'],
            'brightness': ['brightness', 'screen'],
            'type_text': ['type', 'write', 'enter text'],
            'press_key': ['press', 'hit key', 'key press'],

            'set_alarm': ['alarm', 'wake me'],
            'set_reminder': ['remind', 'reminder'],
            'create_todo': ['todo', 'task', 'add task'],
            'list_todos': ['list tasks', 'show tasks', 'my tasks'],
            'set_timer': ['timer', 'countdown'],
            'complete_todo': ['complete', 'done', 'finish task'],
            'delete_todo': ['delete task', 'remove task'],

            'send_whatsapp': ['whatsapp', 'message'],
            'send_email': ['email', 'mail'],

            'weather': ['weather', 'temperature'],
            'time': ['time', 'what time'],
            'date': ['date', 'what date', 'today'],
            'news': ['news', 'headlines'],
            'search': ['search', 'look up', 'google'],
            'wikipedia': ['wikipedia', 'wiki'],

            'greeting': ['hello', 'hi', 'hey'],
            'thanks': ['thank', 'thanks'],
            'goodbye': ['bye', 'goodbye'],
            'help': ['help', 'what can you do']
        }
        
        self.app_aliases = {
            'chrome': 'google chrome',
            'browser': 'google chrome',
            'notepad': 'notepad',
            'calculator': 'calculator',
            'calc': 'calculator'
        }
        
        print("[NLP] Initialized")
    
    def extract_intent(self, text: str) -> str:
        """Extract intent from text."""
        text_lower = text.lower().strip()
        
        for intent, keywords in self.intent_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent
        
        return 'general_query'
    
    def extract_entities(self, text: str, intent: str) -> Dict:
        """Extract entities based on intent."""
        text_lower = text.lower().strip()
        entities = {}
        
        if intent in ['open_app', 'close_app']:
            entities['app_name'] = self._extract_app_name(text_lower)
        
        if intent in ['send_whatsapp', 'send_email']:
            entities['recipient'] = self._extract_recipient(text_lower)
            entities['message'] = self._extract_message(text_lower)
        
        if intent in ['set_alarm', 'set_reminder', 'set_timer']:
            time_info = self._extract_time(text_lower)
            entities.update(time_info)
        
        if intent in ['create_todo', 'set_reminder']:
            entities['task'] = self._extract_task(text_lower)
        
        if intent in ['search', 'wikipedia']:
            entities['query'] = self._extract_query(text_lower)
        
        if intent in ['complete_todo', 'delete_todo']:
            entities['task_id'] = self._extract_task_id(text_lower)

        if intent == 'type_text':
            entities['text'] = self._extract_text_to_type(text_lower)

        if intent == 'press_key':
            entities['key'] = self._extract_key_to_press(text_lower)

        return entities
    
    def _extract_app_name(self, text: str) -> str:
        """Extract app name."""
        for alias, full in self.app_aliases.items():
            if alias in text:
                return full
        
        patterns = [r'open\s+(\w+)', r'close\s+(\w+)']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_recipient(self, text: str) -> str:
        """Extract recipient."""
        match = re.search(r'(?:to|message)\s+(\w+)', text)
        return match.group(1) if match else ""
    
    def _extract_message(self, text: str) -> str:
        """Extract message."""
        match = re.search(r'(?:saying|message|text)\s+(.+)', text)
        return match.group(1).strip() if match else ""
    
    def _extract_time(self, text: str) -> Dict:
        """Extract time info."""
        info = {}
        
        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            period = match.group(3)
            
            if period and 'pm' in period and hour != 12:
                hour += 12
            elif period and 'am' in period and hour == 12:
                hour = 0
            
            info['hour'] = hour
            info['minute'] = minute
        
        # Duration for timers
        match = re.search(r'(\d+)\s*(hour|minute|second)s?', text)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'hour':
                info['duration_seconds'] = value * 3600
            elif unit == 'minute':
                info['duration_seconds'] = value * 60
            else:
                info['duration_seconds'] = value
        
        return info
    
    def _extract_task(self, text: str) -> str:
        """Extract task description."""
        remove = ['todo', 'task', 'remind', 'reminder', 'create', 'add']
        clean = text
        for word in remove:
            clean = clean.replace(word, '')
        return clean.strip()
    
    def _extract_query(self, text: str) -> str:
        """Extract search query."""
        patterns = [r'search\s+(?:for\s+)?(.+)', r'look\s+up\s+(.+)', r'wiki\s+(.+)']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return text.strip()
    
    def _extract_level(self, text: str) -> int:
        """Extract level (0-100)."""
        match = re.search(r'(\d+)\s*(?:percent|%)', text)
        if match:
            return int(match.group(1))
        
        if any(w in text for w in ['max', 'full', 'hundred']):
            return 100
        if any(w in text for w in ['min', 'zero']):
            return 0
        if any(w in text for w in ['half', 'fifty']):
            return 50
        
        return None
    
    def _extract_task_id(self, text: str) -> int:
        """Extract task ID."""
        match = re.search(r'(?:task|number)\s*(\d+)', text)
        return int(match.group(1)) if match else None

    def _extract_text_to_type(self, text: str) -> str:
        """Extract text to type."""
        patterns = [
            r'type\s+(.+)',
            r'write\s+(.+)',
            r'enter\s+(.+)',
            r'input\s+(.+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""

    def _extract_key_to_press(self, text: str) -> str:
        """Extract key to press."""
        patterns = [
            r'press\s+(\w+)',
            r'hit\s+(\w+)',
            r'key\s+(\w+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""

    def process(self, text: str) -> Tuple[str, Dict]:
        """Main processing."""
        if not text:
            return 'unknown', {}
        
        intent = self.extract_intent(text)
        entities = self.extract_entities(text, intent)
        
        return intent, entities