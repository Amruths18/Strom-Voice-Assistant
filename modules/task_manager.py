"""
Task Manager Module for Strom AI Assistant
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict
import threading
import time


class TaskManager:
    """
    Manages tasks, reminders, alarms, timers.
    """
    
    def __init__(self, tasks_file: str = "data/user_tasks.json", reminders_file: str = "data/reminders.json"):
        """Initialize task manager."""
        self.tasks_file = tasks_file
        self.reminders_file = reminders_file
        self.tasks = []
        self.reminders = []
        
        self._load_tasks()
        self._load_reminders()
        print("[TaskManager] Initialized")
    
    def _load_tasks(self):
        """Load tasks."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
    
    def _save_tasks(self):
        """Save tasks."""
        try:
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except:
            pass
    
    def _load_reminders(self):
        """Load reminders."""
        if os.path.exists(self.reminders_file):
            try:
                with open(self.reminders_file, 'r') as f:
                    self.reminders = json.load(f)
            except:
                self.reminders = []
    
    def _save_reminders(self):
        """Save reminders."""
        try:
            os.makedirs(os.path.dirname(self.reminders_file), exist_ok=True)
            with open(self.reminders_file, 'w') as f:
                json.dump(self.reminders, f, indent=2)
        except:
            pass
    
    def create_todo(self, entities: Dict) -> str:
        """Create todo."""
        task = entities.get('task', '').strip()
        
        if not task:
            return "What task should I add?"
        
        self.tasks.append({
            'id': len(self.tasks) + 1,
            'description': task,
            'created_at': datetime.now().isoformat(),
            'completed': False
        })
        
        self._save_tasks()
        return f"Added task: {task}"
    
    def list_todos(self, entities: Dict) -> str:
        """List todos."""
        if not self.tasks:
            return "No tasks yet."
        
        pending = [t for t in self.tasks if not t['completed']]
        
        if not pending:
            return "No pending tasks!"
        
        result = f"You have {len(pending)} tasks:\n"
        for i, task in enumerate(pending, 1):
            result += f"{i}. {task['description']}\n"
        
        return result.strip()
    
    def set_alarm(self, entities: Dict) -> str:
        """Set alarm."""
        hour = entities.get('hour')
        minute = entities.get('minute', 0)
        
        if hour is None:
            return "What time for the alarm?"
        
        now = datetime.now()
        alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if alarm_time <= now:
            alarm_time += timedelta(days=1)
        
        self.reminders.append({
            'type': 'alarm',
            'time': alarm_time.isoformat(),
            'message': 'Alarm!',
            'triggered': False
        })
        
        self._save_reminders()
        return f"Alarm set for {alarm_time.strftime('%I:%M %p')}."
    
    def set_reminder(self, entities: Dict) -> str:
        """Set reminder."""
        task = entities.get('task', '').strip()
        hour = entities.get('hour')
        minute = entities.get('minute', 0)
        
        if not task:
            return "What should I remind you about?"
        
        now = datetime.now()
        
        if hour is not None:
            remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if remind_time <= now:
                remind_time += timedelta(days=1)
        else:
            remind_time = now + timedelta(hours=1)
        
        self.reminders.append({
            'type': 'reminder',
            'time': remind_time.isoformat(),
            'message': task,
            'triggered': False
        })
        
        self._save_reminders()
        return f"Reminder set: {task} at {remind_time.strftime('%I:%M %p')}."
    
    def set_timer(self, entities: Dict) -> str:
        """Set timer."""
        duration = entities.get('duration_seconds')
        
        if not duration:
            return "How long for the timer?"
        
        def timer_thread():
            time.sleep(duration)
            print(f"\n⏰ TIMER: {duration} seconds elapsed!")
        
        threading.Thread(target=timer_thread, daemon=True).start()
        
        if duration >= 60:
            mins = duration // 60
            return f"Timer set for {mins} minute{'s' if mins > 1 else ''}."
        else:
            return f"Timer set for {duration} seconds."
    
    def complete_todo(self, entities: Dict) -> str:
        """Mark todo as complete."""
        task_id = entities.get('task_id')
        
        if task_id is None:
            return "Which task number should I mark complete?"
        
        try:
            task_id = int(task_id) - 1  # Convert to 0-based index
            if 0 <= task_id < len(self.tasks):
                if not self.tasks[task_id]['completed']:
                    self.tasks[task_id]['completed'] = True
                    self._save_tasks()
                    return f"Marked task complete: {self.tasks[task_id]['description']}"
                else:
                    return "Task already completed."
            else:
                return "Invalid task number."
        except:
            return "Invalid task number."
    
    def delete_todo(self, entities: Dict) -> str:
        """Delete todo."""
        task_id = entities.get('task_id')
        
        if task_id is None:
            return "Which task number should I delete?"
        
        try:
            task_id = int(task_id) - 1  # Convert to 0-based index
            if 0 <= task_id < len(self.tasks):
                task = self.tasks.pop(task_id)
                self._save_tasks()
                return f"Deleted task: {task['description']}"
            else:
                return "Invalid task number."
        except:
            return "Invalid task number."