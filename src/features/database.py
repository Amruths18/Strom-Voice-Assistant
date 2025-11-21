# File: src/features/database.py
import sqlite3
from src.config import DB_PATH
from src.core.speaker import speak

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS todos (task TEXT)''')
    conn.commit()
    conn.close()

def add_task(task):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO todos VALUES (?)", (task,))
    conn.commit()
    conn.close()
    speak(f"Added {task} to your list.")

def show_tasks():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM todos")
    tasks = c.fetchall()
    conn.close()
    
    if not tasks:
        speak("You have no pending tasks.")
    else:
        speak("Here are your tasks:")
        for task in tasks:
            speak(task[0])