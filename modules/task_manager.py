"""
Task Manager Module for Strom AI Assistant
Handles alarms, reminders, to-do tasks, and timers.
Stores tasks persistently in JSON files.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import threading
import time


class TaskManager:
    """
    Manages user tasks, reminders, alarms, and timers.
    Provides persistent storage and scheduled notifications.
    """
    
    def __init__(
        self,
        tasks_file: str = "data/user_tasks.json",
        reminders_file: str = "data/reminders.json"
    ):
        """
        Initialize task manager.
        
        Args:
            tasks_file: Path to tasks JSON file
            reminders_file: Path to reminders JSON file
        """
        self.tasks_file = tasks_file
        self.reminders_file = reminders_file
        self.tasks = []
        self.reminders = []
        self.active_timers = []
        
        # Load existing data
        self._load_tasks()
        self._load_reminders()
        
        # Start background checker for reminders/alarms
        self._start_reminder_checker()
        
        print("[TaskManager] Task manager initialized.")
    
    def _load_tasks(self):
        """Load tasks from file."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
                print(f"[TaskManager] Loaded {len(self.tasks)} tasks.")
            except Exception as e:
                print(f"[TaskManager] Error loading tasks: {str(e)}")
                self.tasks = []
        else:
            self.tasks = []
    
    def _save_tasks(self):
        """Save tasks to file."""
        try:
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"[TaskManager] Error saving tasks: {str(e)}")
    
    def _load_reminders(self):
        """Load reminders from file."""
        if os.path.exists(self.reminders_file):
            try:
                with open(self.reminders_file, 'r') as f:
                    self.reminders = json.load(f)
                print(f"[TaskManager] Loaded {len(self.reminders)} reminders.")
            except Exception as e:
                print(f"[TaskManager] Error loading reminders: {str(e)}")
                self.reminders = []
        else:
            self.reminders = []
    
    def _save_reminders(self):
        """Save reminders to file."""
        try:
            os.makedirs(os.path.dirname(self.reminders_file), exist_ok=True)
            with open(self.reminders_file, 'w') as f:
                json.dump(self.reminders, f, indent=2)
        except Exception as e:
            print(f"[TaskManager] Error saving reminders: {str(e)}")
    
    def create_todo(self, entities: Dict) -> str:
        """
        Create a new to-do task.
        
        Args:
            entities: Must contain 'task' (description)
            
        Returns:
            Status message
        """
        task_text = entities.get('task', '').strip()
        
        if not task_text:
            return "Please tell me what task you want to add."
        
        task = {
            'id': len(self.tasks) + 1,
            'description': task_text,
            'created_at': datetime.now().isoformat(),
            'completed': False
        }
        
        self.tasks.append(task)
        self._save_tasks()
        
        return f"Task added: {task_text}"
    
    def list_todos(self, entities: Dict) -> str:
        """
        List all to-do tasks.
        
        Args:
            entities: Command entities (unused)
            
        Returns:
            List of tasks or message if empty
        """
        if not self.tasks:
            return "You have no tasks in your to-do list."
        
        pending_tasks = [t for t in self.tasks if not t['completed']]
        
        if not pending_tasks:
            return "You have no pending tasks. Great job!"
        
        response = f"You have {len(pending_tasks)} pending tasks:\n"
        for i, task in enumerate(pending_tasks, 1):
            response += f"{i}. {task['description']}\n"
        
        return response.strip()
    
    def set_alarm(self, entities: Dict) -> str:
        """
        Set an alarm.
        
        Args:
            entities: Must contain 'hour' and 'minute'
            
        Returns:
            Status message
        """
        hour = entities.get('hour')
        minute = entities.get('minute', 0)
        
        if hour is None:
            return "Please specify the time for the alarm."
        
        # Create alarm time
        now = datetime.now()
        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # If time has passed today, set for tomorrow
        if alarm_time <= now:
            alarm_time += timedelta(days=1)
        
        alarm = {
            'id': len(self.reminders) + 1,
            'type': 'alarm',
            'time': alarm_time.isoformat(),
            'message': 'Alarm ringing!',
            'triggered': False
        }
        
        self.reminders.append(alarm)
        self._save_reminders()
        
        time_str = alarm_time.strftime("%I:%M %p")
        return f"Alarm set for {time_str}."
    
    def set_reminder(self, entities: Dict) -> str:
        """
        Set a reminder.
        
        Args:
            entities: Must contain 'task' and optionally 'hour'/'minute'
            
        Returns:
            Status message
        """
        task_text = entities.get('task', '').strip()
        hour = entities.get('hour')
        minute = entities.get('minute', 0)
        
        if not task_text:
            return "Please tell me what to remind you about."
        
        # Determine reminder time
        now = datetime.now()
        
        if hour is not None:
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if reminder_time <= now:
                reminder_time += timedelta(days=1)
        else:
            # Default to 1 hour from now if no time specified
            reminder_time = now + timedelta(hours=1)
        
        reminder = {
            'id': len(self.reminders) + 1,
            'type': 'reminder',
            'time': reminder_time.isoformat(),
            'message': task_text,
            'triggered': False
        }
        
        self.reminders.append(reminder)
        self._save_reminders()
        
        time_str = reminder_time.strftime("%I:%M %p on %B %d")
        return f"Reminder set: {task_text} at {time_str}."
    
    def set_timer(self, entities: Dict) -> str:
        """
        Set a countdown timer.
        
        Args:
            entities: Must contain 'duration_seconds'
            
        Returns:
            Status message
        """
        duration = entities.get('duration_seconds')
        
        if not duration:
            return "Please specify the timer duration."
        
        # Start timer in background thread
        timer_thread = threading.Thread(
            target=self._run_timer,
            args=(duration,),
            daemon=True
        )
        timer_thread.start()
        self.active_timers.append(timer_thread)
        
        # Format duration message
        if duration >= 3600:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            duration_str = f"{hours} hour{'s' if hours > 1 else ''} and {minutes} minute{'s' if minutes != 1 else ''}"
        elif duration >= 60:
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes} minute{'s' if minutes > 1 else ''}" + (f" and {seconds} seconds" if seconds > 0 else "")
        else:
            duration_str = f"{duration} seconds"
        
        return f"Timer set for {duration_str}."
    
    def _run_timer(self, duration: int):
        """Run timer in background thread."""
        time.sleep(duration)
        print(f"\n[TaskManager] ⏰ TIMER: Time's up! ({duration} seconds elapsed)")
        # In a real implementation, this would trigger TTS notification
    
    def _start_reminder_checker(self):
        """Start background thread to check for due reminders."""
        checker_thread = threading.Thread(
            target=self._check_reminders_loop,
            daemon=True
        )
        checker_thread.start()
    
    def _check_reminders_loop(self):
        """Continuously check for due reminders/alarms."""
        while True:
            try:
                now = datetime.now()
                
                for reminder in self.reminders:
                    if reminder['triggered']:
                        continue
                    
                    reminder_time = datetime.fromisoformat(reminder['time'])
                    
                    # Check if reminder is due (within 1 minute)
                    if now >= reminder_time:
                        reminder['triggered'] = True
                        self._trigger_reminder(reminder)
                        self._save_reminders()
                
                # Check every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                print(f"[TaskManager] Error in reminder checker: {str(e)}")
                time.sleep(60)
    
    def _trigger_reminder(self, reminder: Dict):
        """Trigger a reminder notification."""
        reminder_type = reminder['type']
        message = reminder['message']
        
        print(f"\n[TaskManager] 🔔 {reminder_type.upper()}: {message}")
        # In a real implementation, this would trigger TTS notification


# Test function
def _test_task_manager():
    """Test task manager functionality."""
    
    print("=== Strom Task Manager Test ===\n")
    
    task_mgr = TaskManager(
        tasks_file="data/test_tasks.json",
        reminders_file="data/test_reminders.json"
    )
    
    # Test creating tasks
    print("Creating tasks...")
    print(task_mgr.create_todo({'task': 'Buy groceries'}))
    print(task_mgr.create_todo({'task': 'Finish project report'}))
    print(task_mgr.create_todo({'task': 'Call dentist'}))
    
    # Test listing tasks
    print("\n" + task_mgr.list_todos({}))
    
    # Test setting alarm
    print("\nSetting alarm...")
    print(task_mgr.set_alarm({'hour': 7, 'minute': 30}))
    
    # Test setting reminder
    print("\nSetting reminder...")
    print(task_mgr.set_reminder({'task': 'Team meeting', 'hour': 14, 'minute': 0}))
    
    # Test timer
    print("\nSetting 5-second timer...")
    print(task_mgr.set_timer({'duration_seconds': 5}))
    
    print("\nWaiting for timer...")
    time.sleep(6)
    
    print("\n✅ Task Manager Test Complete!")


if __name__ == "__main__":
    _test_task_manager()