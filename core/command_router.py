"""
Command Router for Strom AI Assistant
Routes intents to appropriate modules
"""

from typing import Dict, Any


class CommandRouter:
    """
    Routes commands to module handlers.
    """
    
    def __init__(self):
        """Initialize router."""
        self.modules = {}
        self.route_map = {}
        print("[Router] Initialized")
    
    def register_module(self, name: str, instance: Any):
        """Register a module."""
        self.modules[name] = instance
        print(f"[Router] Registered: {name}")
    
    def register_routes(self):
        """Map intents to modules."""
        self.route_map = {
            'shutdown': ('system_control', 'shutdown'),
            'restart': ('system_control', 'restart'),
            'lock': ('system_control', 'lock_screen'),
            'sleep': ('system_control', 'sleep'),
            'open_app': ('system_control', 'open_application'),
            'close_app': ('system_control', 'close_application'),
            'volume': ('system_control', 'control_volume'),
            'brightness': ('system_control', 'control_brightness'),
            'screenshot': ('system_control', 'take_screenshot'),
            'system_info': ('system_control', 'get_system_info'),
            
            'set_alarm': ('task_manager', 'set_alarm'),
            'set_reminder': ('task_manager', 'set_reminder'),
            'create_todo': ('task_manager', 'create_todo'),
            'list_todos': ('task_manager', 'list_todos'),
            'set_timer': ('task_manager', 'set_timer'),
            'complete_todo': ('task_manager', 'complete_todo'),
            'delete_todo': ('task_manager', 'delete_todo'),
            
            'send_whatsapp': ('messaging', 'send_whatsapp'),
            'send_email': ('messaging', 'send_email'),
            
            'weather': ('general_knowledge', 'get_weather'),
            'time': ('general_knowledge', 'get_time'),
            'date': ('general_knowledge', 'get_date'),
            'news': ('general_knowledge', 'get_news'),
            'search': ('general_knowledge', 'web_search'),
            'wikipedia': ('general_knowledge', 'wikipedia_search'),
            'general_query': ('general_knowledge', 'answer_query'),
            
            'greeting': ('router', 'handle_greeting'),
            'thanks': ('router', 'handle_thanks'),
            'goodbye': ('router', 'handle_goodbye'),
            'help': ('router', 'handle_help')
        }
    
    def route(self, intent: str, entities: Dict) -> str:
        """Route command to module."""
        if intent not in self.route_map:
            return "I didn't understand that."
        
        module_name, method_name = self.route_map[intent]
        
        # Handle internal commands
        if module_name == 'router':
            return self._handle_internal(method_name)
        
        # Check if module exists
        if module_name not in self.modules:
            return f"Module {module_name} not available."
        
        # Execute
        try:
            module = self.modules[module_name]
            method = getattr(module, method_name)
            return method(entities)
        except Exception as e:
            print(f"[Router] Error: {str(e)}")
            return "Sorry, I encountered an error."
    
    def _handle_internal(self, command: str) -> str:
        """Handle conversation commands."""
        responses = {
            'handle_greeting': "Hello! I'm Strom. How can I help?",
            'handle_thanks': "You're welcome!",
            'handle_goodbye': "Goodbye! Have a great day!",
            'handle_help': "I can help with system control, tasks, messaging, and information. Just ask!"
        }
        return responses.get(command, "I'm here to help.")


if __name__ == "__main__":
    router = CommandRouter()
    router.register_routes()
    print(router.route('greeting', {}))