"""
Security Module for Strom AI Assistant
"""

from typing import Dict, Tuple


class Security:
    """
    Security validation and protection.
    """
    
    def __init__(self):
        """Initialize security."""
        self.dangerous_commands = ['shutdown', 'restart', 'delete']
        print("[Security] Initialized")
    
    def validate_command(self, intent: str, entities: Dict) -> Tuple[bool, str]:
        """Validate command safety."""
        if intent in ['shutdown', 'restart']:
            return True, "Proceeding..."
        
        return True, "OK"
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize input."""
        dangerous = [';', '|', '&', '`', '$']
        
        for char in dangerous:
            text = text.replace(char, '')
        
        return text.strip()
    
    def log_command(self, intent: str, entities: Dict):
        """Log command."""
        print(f"[Security] Command: {intent}")