"""
Validator Module for Strom AI Assistant
"""

from typing import Optional, Tuple


class Validator:
    """
    Input validation.
    """
    
    def __init__(self):
        """Initialize validator."""
        print("[Validator] Initialized")
    
    def validate_time(self, hour: Optional[int], minute: Optional[int] = 0) -> Tuple[bool, str]:
        """Validate time."""
        if hour is None:
            return False, "Hour required."
        
        if not (0 <= hour <= 23):
            return False, f"Invalid hour: {hour}"
        
        if minute is not None and not (0 <= minute <= 59):
            return False, f"Invalid minute: {minute}"
        
        return True, "Valid"
    
    def validate_duration(self, duration: Optional[int]) -> Tuple[bool, str]:
        """Validate duration."""
        if duration is None:
            return False, "Duration required."
        
        if duration <= 0:
            return False, "Duration must be positive."
        
        if duration > 86400:
            return False, "Duration too long."
        
        return True, "Valid"