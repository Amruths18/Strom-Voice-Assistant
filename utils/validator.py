"""
Validator Module for Strom AI Assistant
Validates dates, times, and command parameters.
Ensures data integrity before processing.
"""

from datetime import datetime, timedelta
import re
from typing import Optional, Tuple


class Validator:
    """
    Validates various types of user input and command parameters.
    """
    
    def __init__(self):
        """Initialize validator."""
        print("[Validator] Validator initialized.")
    
    def validate_time(self, hour: Optional[int], minute: Optional[int] = 0) -> Tuple[bool, str]:
        """
        Validate time values.
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if hour is None:
            return False, "Hour is required."
        
        if not (0 <= hour <= 23):
            return False, f"Invalid hour: {hour}. Must be between 0 and 23."
        
        if minute is not None and not (0 <= minute <= 59):
            return False, f"Invalid minute: {minute}. Must be between 0 and 59."
        
        return True, "Valid time."
    
    def validate_date(self, date_str: str) -> Tuple[bool, str, Optional[datetime]]:
        """
        Validate and parse date string.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Tuple of (is_valid, message, parsed_datetime)
        """
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%B %d, %Y',
            '%d %B %Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return True, "Valid date.", dt
            except ValueError:
                continue
        
        return False, f"Invalid date format: {date_str}", None
    
    def validate_duration(self, duration_seconds: Optional[int]) -> Tuple[bool, str]:
        """
        Validate duration value.
        
        Args:
            duration_seconds: Duration in seconds
            
        Returns:
            Tuple of (is_valid, message)
        """
        if duration_seconds is None:
            return False, "Duration is required."
        
        if duration_seconds <= 0:
            return False, "Duration must be positive."
        
        if duration_seconds > 86400:  # More than 24 hours
            return False, "Duration cannot exceed 24 hours."
        
        return True, "Valid duration."
    
    def validate_volume_level(self, level: Optional[int]) -> Tuple[bool, str]:
        """
        Validate volume level.
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if level is None:
            return False, "Volume level is required."
        
        if not (0 <= level <= 100):
            return False, f"Invalid volume level: {level}. Must be between 0 and 100."
        
        return True, "Valid volume level."
    
    def validate_app_name(self, app_name: str) -> Tuple[bool, str]:
        """
        Validate application name.
        
        Args:
            app_name: Application name
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not app_name or app_name.strip() == '':
            return False, "Application name cannot be empty."
        
        if app_name.lower() == 'unknown':
            return False, "Please specify a valid application name."
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '/', '\\', 'rm ', 'del ']
        if any(pattern in app_name.lower() for pattern in dangerous_patterns):
            return False, "Invalid application name."
        
        return True, "Valid application name."
    
    def validate_message(self, message: str, max_length: int = 1000) -> Tuple[bool, str]:
        """
        Validate message content.
        
        Args:
            message: Message text
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not message or message.strip() == '':
            return False, "Message cannot be empty."
        
        if len(message) > max_length:
            return False, f"Message too long. Maximum {max_length} characters."
        
        return True, "Valid message."
    
    def parse_relative_time(self, text: str) -> Optional[datetime]:
        """
        Parse relative time expressions like "in 5 minutes", "tomorrow at 3pm".
        
        Args:
            text: Time expression
            
        Returns:
            Parsed datetime or None
        """
        text_lower = text.lower()
        now = datetime.now()
        
        # Handle "in X minutes/hours"
        match = re.search(r'in (\d+) (minute|hour|second)s?', text_lower)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'second':
                return now + timedelta(seconds=value)
            elif unit == 'minute':
                return now + timedelta(minutes=value)
            elif unit == 'hour':
                return now + timedelta(hours=value)
        
        # Handle "tomorrow"
        if 'tomorrow' in text_lower:
            tomorrow = now + timedelta(days=1)
            
            # Check for time
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text_lower)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                period = time_match.group(3)
                
                if period and period == 'pm' and hour != 12:
                    hour += 12
                elif period and period == 'am' and hour == 12:
                    hour = 0
                
                return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Handle "today"
        if 'today' in text_lower:
            return now
        
        return None
    
    def is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string
            
        Returns:
            True if valid, False otherwise
        """
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return pattern.match(url) is not None


# Test function
def _test_validator():
    """Test validator module."""
    
    print("=== Strom Validator Module Test ===\n")
    
    validator = Validator()
    
    # Test time validation
    print("Time Validation:")
    times = [(7, 30), (25, 0), (14, 75)]
    for hour, minute in times:
        is_valid, message = validator.validate_time(hour, minute)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {hour}:{minute:02d} - {message}")
    print()
    
    # Test duration validation
    print("Duration Validation:")
    durations = [300, -10, 90000]
    for duration in durations:
        is_valid, message = validator.validate_duration(duration)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {duration}s - {message}")
    print()
    
    # Test relative time parsing
    print("Relative Time Parsing:")
    expressions = ["in 5 minutes", "tomorrow at 3pm", "in 2 hours"]
    for expr in expressions:
        result = validator.parse_relative_time(expr)
        if result:
            print(f"  ✅ '{expr}' -> {result.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  ❌ '{expr}' -> Could not parse")


if __name__ == "__main__":
    _test_validator()