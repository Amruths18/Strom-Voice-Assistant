"""
Security Module for Strom AI Assistant
Prevents dangerous or unauthorized system operations.
Validates commands before execution.
"""

import os
from typing import Dict, Tuple


class Security:
    """
    Provides security checks and validations for system commands.
    Prevents potentially harmful operations.
    """
    
    def __init__(self):
        """Initialize security module."""
        # Dangerous commands that require confirmation
        self.dangerous_commands = [
            'shutdown',
            'restart',
            'delete',
            'format',
            'remove'
        ]
        
        # Protected system paths
        self.protected_paths = [
            '/system',
            '/windows',
            'C:\\Windows',
            'C:\\System32',
            '/bin',
            '/sbin',
            '/usr/bin'
        ]
        
        print("[Security] Security module initialized.")
    
    def validate_command(self, intent: str, entities: Dict) -> Tuple[bool, str]:
        """
        Validate if a command is safe to execute.
        
        Args:
            intent: Command intent
            entities: Command entities
            
        Returns:
            Tuple of (is_valid, message)
        """
        # Check for dangerous system commands
        if intent in ['shutdown', 'restart']:
            return True, "Command requires confirmation. Proceeding..."
        
        # Validate file/app operations
        if intent in ['open_app', 'close_app']:
            app_name = entities.get('app_name', '').lower()
            
            # Block system-critical processes
            blocked_apps = ['system', 'kernel', 'init', 'systemd', 'explorer']
            if any(blocked in app_name for blocked in blocked_apps):
                return False, f"Cannot operate on system-critical process: {app_name}"
        
        # Validate file paths (if file operations were implemented)
        if 'path' in entities:
            path = entities['path']
            if self._is_protected_path(path):
                return False, f"Access denied to protected path: {path}"
        
        return True, "Command validated."
    
    def _is_protected_path(self, path: str) -> bool:
        """
        Check if path is protected.
        
        Args:
            path: File system path
            
        Returns:
            True if protected, False otherwise
        """
        path_lower = path.lower()
        
        for protected in self.protected_paths:
            if protected.lower() in path_lower:
                return True
        
        return False
    
    def require_confirmation(self, intent: str) -> bool:
        """
        Check if command requires user confirmation.
        
        Args:
            intent: Command intent
            
        Returns:
            True if confirmation required
        """
        return intent in self.dangerous_commands
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            text: User input text
            
        Returns:
            Sanitized text
        """
        # Remove potentially dangerous characters
        dangerous_chars = [';', '|', '&', '`', '$', '(', ')']
        
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address
            
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number
            
        Returns:
            True if valid, False otherwise
        """
        import re
        # Basic validation for international format
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None
    
    def log_command(self, intent: str, entities: Dict, user: str = "default"):
        """
        Log executed commands for audit trail.
        
        Args:
            intent: Command intent
            entities: Command entities
            user: Username (for multi-user systems)
        """
        from datetime import datetime
        
        log_entry = f"[{datetime.now().isoformat()}] User: {user} | Intent: {intent} | Entities: {entities}"
        
        # In production, write to secure log file
        print(f"[Security] {log_entry}")


# Test function
def _test_security():
    """Test security module."""
    
    print("=== Strom Security Module Test ===\n")
    
    security = Security()
    
    # Test command validation
    test_cases = [
        ('shutdown', {}, "Shutdown command"),
        ('open_app', {'app_name': 'chrome'}, "Open Chrome"),
        ('open_app', {'app_name': 'system'}, "Open system process"),
    ]
    
    for intent, entities, description in test_cases:
        print(f"Test: {description}")
        is_valid, message = security.validate_command(intent, entities)
        print(f"  Valid: {is_valid}")
        print(f"  Message: {message}\n")
    
    # Test email validation
    emails = ['user@example.com', 'invalid-email', 'test@domain']
    print("Email Validation:")
    for email in emails:
        is_valid = security.validate_email(email)
        print(f"  {email}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    print()
    
    # Test input sanitization
    dangerous_input = "delete file; rm -rf /"
    sanitized = security.sanitize_input(dangerous_input)
    print(f"Input Sanitization:")
    print(f"  Original: {dangerous_input}")
    print(f"  Sanitized: {sanitized}")


if __name__ == "__main__":
    _test_security()