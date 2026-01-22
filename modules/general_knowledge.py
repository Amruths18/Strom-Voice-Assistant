"""
General Knowledge Module for Strom AI Assistant
"""

import requests
from datetime import datetime
from typing import Dict, Optional
import webbrowser
import urllib.parse


class GeneralKnowledge:
    """
    Provides information and answers.
    """
    
    def __init__(self, weather_api_key: Optional[str] = None, news_api_key: Optional[str] = None):
        """Initialize general knowledge."""
        self.weather_api_key = weather_api_key
        self.news_api_key = news_api_key
        print("[GeneralKnowledge] Initialized")
    
    def is_online(self) -> bool:
        """Check internet."""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def get_time(self, entities: Dict) -> str:
        """Get current time."""
        now = datetime.now()
        return f"It's {now.strftime('%I:%M %p')}."
    
    def get_date(self, entities: Dict) -> str:
        """Get current date."""
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."
    
    def get_weather(self, entities: Dict) -> str:
        """Get weather."""
        if not self.is_online():
            return "I need internet for weather."
        
        if not self.weather_api_key:
            return "Weather API not configured."
        
        return "Weather feature requires API configuration."
    
    def get_news(self, entities: Dict) -> str:
        """Get news."""
        if not self.is_online():
            return "I need internet for news."
        
        if not self.news_api_key:
            return "News API not configured."
        
        return "News feature requires API configuration."
    
    def web_search(self, entities: Dict) -> str:
        """Web search."""
        query = entities.get('query', '').strip()
        
        if not query:
            return "What should I search for?"
        
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching for: {query}"
        except:
            return "Failed to open browser."
    
    def wikipedia_search(self, entities: Dict) -> str:
        """Wikipedia search."""
        query = entities.get('query', '').strip()
        
        if not query:
            return "What should I look up?"
        
        if not self.is_online():
            return "I need internet for Wikipedia."
        
        try:
            import wikipedia
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except:
            return f"Couldn't find information about {query}."
    
    def answer_query(self, entities: Dict) -> str:
        """Answer general query."""
        return "I'm not sure about that. Would you like me to search?"