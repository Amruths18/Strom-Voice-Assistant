"""
Strom AI Assistant - Automation Capabilities Demo
Showcases all the efficient automation tasks Strom can perform
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.nlp_engine import NLPEngine
from core.command_router import CommandRouter
from modules.system_control import SystemControl
from modules.task_manager import TaskManager
from modules.messaging import Messaging
from modules.general_knowledge import GeneralKnowledge

def demo_system_control():
    """Demo system control automation."""
    print("\n" + "="*60)
    print("  🔧 SYSTEM CONTROL AUTOMATION")
    print("="*60)

    router = CommandRouter()
    router.register_module('system_control', SystemControl())

    commands = [
        "open notepad",
        "open calculator",
        "open chrome",
        "take screenshot",
        "get system info",
        "set volume to 50 percent",
        "lock screen"
    ]

    print("Available System Commands:")
    for cmd in commands:
        print(f"  • '{cmd}'")
    print("\n💡 Try saying these commands to Strom!")

def demo_task_management():
    """Demo task management automation."""
    print("\n" + "="*60)
    print("  📋 TASK MANAGEMENT AUTOMATION")
    print("="*60)

    router = CommandRouter()
    task_mgr = TaskManager()
    router.register_module('task_manager', task_mgr)

    # Demo task creation
    print("Creating sample tasks...")
    tasks = [
        "Buy groceries",
        "Finish project report",
        "Call dentist",
        "Exercise for 30 minutes"
    ]

    for task in tasks:
        result = task_mgr.create_todo({'task': task})
        print(f"  ✓ {result}")

    # Demo listing
    print("\nListing tasks:")
    result = task_mgr.list_todos({})
    print(f"  {result}")

    # Demo timer
    print("\nSetting a 5-second timer...")
    result = task_mgr.set_timer({'duration_seconds': 5})
    print(f"  {result}")

    commands = [
        "set alarm for 7 am",
        "remind me to drink water in 1 hour",
        "add task clean the house",
        "list my tasks",
        "complete task number 1",
        "delete task number 3",
        "set timer for 10 minutes"
    ]

    print("\nAvailable Task Commands:")
    for cmd in commands:
        print(f"  • '{cmd}'")
    print("\n💡 Try saying these commands to Strom!")

def demo_messaging():
    """Demo messaging automation."""
    print("\n" + "="*60)
    print("  💬 MESSAGING AUTOMATION")
    print("="*60)

    router = CommandRouter()
    router.register_module('messaging', Messaging())

    commands = [
        "send whatsapp to john saying hello",
        "email to boss saying meeting at 3pm"
    ]

    print("Available Messaging Commands:")
    for cmd in commands:
        print(f"  • '{cmd}'")
    print("\n💡 Try saying these commands to Strom!")
    print("📝 Note: Configure email settings in config/api.yaml for email functionality")

def demo_information():
    """Demo information automation."""
    print("\n" + "="*60)
    print("  🧠 INFORMATION AUTOMATION")
    print("="*60)

    router = CommandRouter()
    router.register_module('general_knowledge', GeneralKnowledge())

    commands = [
        "what time is it",
        "what date is today",
        "search for python tutorials",
        "wikipedia python programming",
        "get weather",
        "show news"
    ]

    print("Available Information Commands:")
    for cmd in commands:
        print(f"  • '{cmd}'")
    print("\n💡 Try saying these commands to Strom!")
    print("📝 Note: Configure API keys in config/api.yaml for weather/news")

def demo_nlp_processing():
    """Demo NLP processing capabilities."""
    print("\n" + "="*60)
    print("  🧠 NATURAL LANGUAGE PROCESSING")
    print("="*60)

    nlp = NLPEngine()

    test_commands = [
        "open google chrome",
        "set alarm for 8 am",
        "remind me to call mom",
        "take a screenshot",
        "what's the system status",
        "shutdown the computer",
        "send email to john",
        "set volume to 75 percent"
    ]

    print("NLP Processing Examples:")
    for cmd in test_commands:
        intent, entities = nlp.process(cmd)
        print(f"  '{cmd}' → Intent: {intent}, Entities: {entities}")

def show_full_capability_list():
    """Show complete list of Strom's capabilities."""
    print("\n" + "="*80)
    print("  🚀 STROM AI ASSISTANT - COMPLETE CAPABILITY LIST")
    print("="*80)

    capabilities = {
        "🎯 System Control": [
            "Shutdown/Restart computer",
            "Lock/Sleep system",
            "Open/Close applications (Notepad, Calculator, Chrome, etc.)",
            "Control volume and brightness",
            "Take screenshots",
            "Get system information (CPU, Memory, Battery)"
        ],

        "📝 Task Management": [
            "Create and manage todo lists",
            "Set alarms and reminders",
            "Set timers and countdowns",
            "Mark tasks complete",
            "Delete tasks"
        ],

        "💬 Communication": [
            "Send WhatsApp messages",
            "Send emails (with configuration)",
            "Open messaging applications"
        ],

        "🧠 Information & Search": [
            "Tell time and date",
            "Web search (opens browser)",
            "Wikipedia lookup",
            "Weather information (with API)",
            "News headlines (with API)"
        ],

        "🎤 Voice Interaction": [
            "Wake word detection ('Hey Strom')",
            "Stop word detection ('Stop Strom')",
            "Continuous listening with silence detection",
            "Voice feedback and responses",
            "Error recovery and retries"
        ]
    }

    for category, features in capabilities.items():
        print(f"\n{category}")
        for feature in features:
            print(f"  ✓ {feature}")

    print(f"\n{'='*80}")
    print("  🎯 HOW TO USE STROM")
    print(f"{'='*80}")
    print("  1. Run: python main.py")
    print("  2. Say: 'Hey Strom' to wake")
    print("  3. Give voice commands naturally")
    print("  4. Say: 'Stop Strom' to deactivate")
    print("  5. Press Ctrl+C to exit")
    print()
    print("  💡 Pro Tips:")
    print("  • Speak clearly and naturally")
    print("  • Wait for Strom to finish responding")
    print("  • Use simple, direct commands")
    print("  • Configure API keys for enhanced features")
    print(f"{'='*80}")

def main():
    """Run the automation demo."""
    print("STROM AI ASSISTANT - AUTOMATION CAPABILITIES DEMO")
    print("Demonstrating efficient automation tasks performed by voice")

    demo_system_control()
    demo_task_management()
    demo_messaging()
    demo_information()
    demo_nlp_processing()
    show_full_capability_list()

    print("\n🎉 Strom is ready to perform these automation tasks with voice commands!")
    print("💡 Start Strom with: python main.py")

if __name__ == "__main__":
    main()