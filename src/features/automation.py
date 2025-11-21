# File: src/features/automation.py
import subprocess
import pyautogui
import datetime
from src.core.speaker import speak

def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {current_time}")

def tell_date():
    today = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"Today is {today}")

def open_notepad():
    speak("Opening Notepad")
    subprocess.Popen(["notepad.exe"])

def open_calculator():
    speak("Opening Calculator")
    subprocess.Popen(["calc.exe"])

def take_screenshot():
    speak("Taking screenshot")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pyautogui.screenshot(f"screenshot_{timestamp}.png")
    speak("Screenshot saved.")