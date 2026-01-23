"""
General Knowledge Module for Strom AI Assistant
"""

import requests
from datetime import datetime
from typing import Dict, Optional
import webbrowser
import urllib.parse
import random


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
        time_str = now.strftime('%I:%M %p')
        
        templates = [
            f"It's currently {time_str}.",
            f"The time is {time_str}.",
            f"It is {time_str} right now.",
            f"Check the clock! It's {time_str}."
        ]
        return random.choice(templates)
    
    def get_date(self, entities: Dict) -> str:
        """Get current date."""
        now = datetime.now()
        date_str = now.strftime('%A, %B %d, %Y')
        
        templates = [
            f"Today is {date_str}.",
            f"It's {date_str}.",
            f"The date today is {date_str}.",
            f"We are in {now.strftime('%B')}, specifically {date_str}."
        ]
        return random.choice(templates)
    
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
            
            templates = [
                f"Searching the web for '{query}'...",
                f"I've looked that up for you. Check your browser for '{query}'.",
                f"Here is what I found for '{query}'.",
                f"Let's see what Google says about '{query}'."
            ]
            return random.choice(templates)
        except:
            return "I tried to open the browser, but something went wrong."
    
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
        templates = [
            "I'm not entirely sure about that. Should I search the web for you?",
            "That's outside my knowledge base right now. Want me to Google it?",
            "I don't have the answer to that yet. Would a web search help?",
            "Hmm, interesting question. I can look it up online if you'd like."
        ]
        return random.choice(templates)