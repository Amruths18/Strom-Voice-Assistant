"""
Command Router for Strom AI Assistant
Routes processed intents to appropriate module handlers.
Acts as the central dispatcher for all commands.
"""

from typing import Dict, Any, Optional


class CommandRouter:
    """
    Routes commands to appropriate module handlers based on intent.
    Manages module initialization and delegates execution.
    """
    
    def __init__(self):
        """Initialize command router."""
        self.modules = {}
        self.route_map = {}
        print("[Router] Command router initialized.")
    
    def register_module(self, module_name: str, module_instance: Any):
        """
        Register a module handler.
        
        Args:
            module_name: Name identifier for the module
            module_instance: Instance of the module class
        """
        self.modules[module_name] = module_instance
        print(f"[Router] Module registered: {module_name}")
    
    def register_routes(self):
        """Map intents to module methods."""
        self.route_map = {
            # System Control routes
            'shutdown': ('system_control', 'shutdown'),
            'restart': ('system_control', 'restart'),
            'lock': ('system_control', 'lock_screen'),
            'sleep': ('system_control', 'sleep'),
            'open_app': ('system_control', 'open_application'),
            'close_app': ('system_control', 'close_application'),
            'volume': ('system_control', 'control_volume'),
            'brightness': ('system_control', 'control_brightness'),
            
            # Task Manager routes
            'set_alarm': ('task_manager', 'set_alarm'),
            'set_reminder': ('task_manager', 'set_reminder'),
            'create_todo': ('task_manager', 'create_todo'),
            'list_todos': ('task_manager', 'list_todos'),
            'set_timer': ('task_manager', 'set_timer'),
            
            # Messaging routes
            'send_whatsapp': ('messaging', 'send_whatsapp'),
            'send_email': ('messaging', 'send_email'),
            
            # General Knowledge routes
            'weather': ('general_knowledge', 'get_weather'),
            'time': ('general_knowledge', 'get_time'),
            'date': ('general_knowledge', 'get_date'),
            'news': ('general_knowledge', 'get_news'),
            'search': ('general_knowledge', 'web_search'),
            'wikipedia': ('general_knowledge', 'wikipedia_search'),
            'general_query': ('general_knowledge', 'answer_query'),
            
            # Conversation routes (handled internally)
            'greeting': ('router', 'handle_greeting'),
            'thanks': ('router', 'handle_thanks'),
            'goodbye': ('router', 'handle_goodbye'),
            'help': ('router', 'handle_help')
        }
        print("[Router] Routes registered.")
    
    def route(self, intent: str, entities: Dict) -> str:
        """
        Route command to appropriate module handler.
        
        Args:
            intent: Detected intent from NLP
            entities: Extracted entities
            
        Returns:
            Response message from handler
        """
        # Check if route exists
        if intent not in self.route_map:
            return self._handle_unknown_intent(intent)
        
        module_name, method_name = self.route_map[intent]
        
        # Handle internal conversation routes
        if module_name == 'router':
            return self._handle_internal_command(method_name, entities)
        
        # Check if module is registered
        if module_name not in self.modules:
            return f"Module {module_name} is not available."
        
        # Get module and method
        module = self.modules[module_name]
        
        if not hasattr(module, method_name):
            return f"Method {method_name} not found in {module_name}."
        
        # Execute method
        try:
            method = getattr(module, method_name)
            response = method(entities)
            return response
        except Exception as e:
            error_msg = f"Error executing {module_name}.{method_name}: {str(e)}"
            print(f"[Router] {error_msg}")
            return "Sorry, I encountered an error while processing your request."
    
    def _handle_internal_command(self, command: str, entities: Dict) -> str:
        """Handle conversation commands internally."""
        responses = {
            'handle_greeting': "Hello! I'm Strom. How can I help you today?",
            'handle_thanks': "You're welcome! Happy to help.",
            'handle_goodbye': "Goodbye! Have a great day!",
            'handle_help': self._get_help_message()
        }
        return responses.get(command, "I'm here to assist you.")
    
    def _get_help_message(self) -> str:
        """Generate help message with available commands."""
        help_text = """I can help you with:
        
System Control: shutdown, restart, lock screen, open apps, control volume and brightness

Tasks: set alarms, reminders, create to-do lists, set timers

Messaging: send WhatsApp messages and emails

Information: weather, time, date, news, web search, and general questions

Just speak naturally and I'll understand!"""
        return help_text
    
    def _handle_unknown_intent(self, intent: str) -> str:
        """Handle unrecognized intents."""
        return "I didn't quite understand that. Could you please rephrase?"
    
    def get_available_modules(self) -> list:
        """
        Get list of registered modules.
        
        Returns:
            List of module names
        """
        return list(self.modules.keys())


# Test function
def _test_command_router():
    """Test command router with mock modules."""
    
    print("=== Strom Command Router Test ===\n")
    
    # Mock module for testing
    class MockSystemControl:
        def shutdown(self, entities):
            return "System shutting down..."
        
        def open_application(self, entities):
            app = entities.get('app_name', 'unknown')
            return f"Opening {app}..."
    
    # Initialize router
    router = CommandRouter()
    
    # Register mock module
    mock_system = MockSystemControl()
    router.register_module('system_control', mock_system)
    router.register_routes()
    
    # Test routing
    test_cases = [
        ('shutdown', {}),
        ('open_app', {'app_name': 'chrome'}),
        ('greeting', {}),
        ('help', {}),
        ('unknown_intent', {})
    ]
    
    for intent, entities in test_cases:
        print(f"Intent: {intent}")
        print(f"Entities: {entities}")
        response = router.route(intent, entities)
        print(f"Response: {response}\n")


if __name__ == "__main__":
    _test_command_router()