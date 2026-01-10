"""
General Knowledge Module for Strom AI Assistant
Handles weather, time, date, news, web search, and general queries.
Uses online APIs when available, falls back to offline responses.
"""

import requests
from datetime import datetime
from typing import Dict, Optional
import wikipedia


class GeneralKnowledge:
    """
    Provides information and answers to general queries.
    Hybrid online/offline operation.
    """
    
    def __init__(
        self,
        weather_api_key: Optional[str] = None,
        news_api_key: Optional[str] = None
    ):
        """
        Initialize general knowledge module.
        
        Args:
            weather_api_key: OpenWeatherMap API key
            news_api_key: News API key
        """
        self.weather_api_key = weather_api_key
        self.news_api_key = news_api_key
        
        print("[GeneralKnowledge] General knowledge module initialized.")
    
    def is_online(self) -> bool:
        """Check internet connectivity."""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def get_time(self, entities: Dict) -> str:
        """
        Get current time.
        
        Args:
            entities: Command entities (unused)
            
        Returns:
            Current time string
        """
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}."
    
    def get_date(self, entities: Dict) -> str:
        """
        Get current date.
        
        Args:
            entities: Command entities (unused)
            
        Returns:
            Current date string
        """
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}."
    
    def get_weather(self, entities: Dict) -> str:
        """
        Get weather information.
        
        Args:
            entities: May contain 'location'
            
        Returns:
            Weather information or error message
        """
        if not self.is_online():
            return "I need internet connection to check the weather."
        
        if not self.weather_api_key:
            return "Weather API is not configured. Please add your OpenWeatherMap API key."
        
        location = entities.get('location', 'current location')
        
        try:
            # Use IP geolocation for current location
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.weather_api_key}&units=metric"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                city = data['name']
                
                return f"The weather in {city} is {description} with a temperature of {temp} degrees Celsius."
            else:
                return "Sorry, I couldn't fetch the weather information."
                
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    def get_news(self, entities: Dict) -> str:
        """
        Get latest news headlines.
        
        Args:
            entities: May contain 'category' or 'query'
            
        Returns:
            News headlines or error message
        """
        if not self.is_online():
            return "I need internet connection to fetch news."
        
        if not self.news_api_key:
            return "News API is not configured. Please add your News API key."
        
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.news_api_key}"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])[:5]
                
                if not articles:
                    return "No news articles found."
                
                news_text = "Here are the top news headlines:\n"
                for i, article in enumerate(articles, 1):
                    title = article['title']
                    news_text += f"{i}. {title}\n"
                
                return news_text.strip()
            else:
                return "Sorry, I couldn't fetch news at the moment."
                
        except Exception as e:
            return f"Error getting news: {str(e)}"
    
    def web_search(self, entities: Dict) -> str:
        """
        Perform web search.
        
        Args:
            entities: Must contain 'query'
            
        Returns:
            Search result summary
        """
        query = entities.get('query', '').strip()
        
        if not query:
            return "Please tell me what to search for."
        
        if not self.is_online():
            return "I need internet connection to search the web."
        
        # Open browser with search query
        import webbrowser
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        
        return f"Opening web search for: {query}"
    
    def wikipedia_search(self, entities: Dict) -> str:
        """
        Search Wikipedia for information.
        
        Args:
            entities: Must contain 'query'
            
        Returns:
            Wikipedia summary
        """
        query = entities.get('query', '').strip()
        
        if not query:
            return "Please tell me what to look up on Wikipedia."
        
        if not self.is_online():
            return "I need internet connection to access Wikipedia."
        
        try:
            # Set language
            wikipedia.set_lang('en')
            
            # Search Wikipedia
            summary = wikipedia.summary(query, sentences=3)
            
            return summary
            
        except wikipedia.exceptions.DisambiguationError as e:
            options = ', '.join(e.options[:5])
            return f"Multiple results found. Did you mean: {options}?"
        
        except wikipedia.exceptions.PageError:
            return f"Sorry, I couldn't find any information about {query} on Wikipedia."
        
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"
    
    def answer_query(self, entities: Dict) -> str:
        """
        Answer general queries using basic knowledge.
        
        Args:
            entities: Query context
            
        Returns:
            Answer or suggestion to search
        """
        # Offline fallback responses
        offline_responses = [
            "I'm not sure about that. Would you like me to search the web?",
            "I don't have that information right now. Try asking me to search for it.",
            "That's beyond my offline knowledge. I can search online if you'd like."
        ]
        
        import random
        return random.choice(offline_responses)


# Test function
def _test_general_knowledge():
    """Test general knowledge module."""
    
    print("=== Strom General Knowledge Test ===\n")
    
    gk = GeneralKnowledge()
    
    # Test time
    print("Test 1: Get Time")
    print(gk.get_time({}))
    print()
    
    # Test date
    print("Test 2: Get Date")
    print(gk.get_date({}))
    print()
    
    # Test Wikipedia
    print("Test 3: Wikipedia Search")
    result = gk.wikipedia_search({'query': 'Python programming language'})
    print(result[:200] + "...")
    print()


if __name__ == "__main__":
    _test_general_knowledge()