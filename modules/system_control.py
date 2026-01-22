"""
System Control Module for Strom AI Assistant
"""

import os
import platform
import subprocess
import psutil
from typing import Dict


class SystemControl:
    """
    Manages system-level operations.
    """
    
    def __init__(self):
        """Initialize system control."""
        self.system = platform.system()
        print(f"[SystemControl] Initialized ({self.system})")
    
    def shutdown(self, entities: Dict) -> str:
        """Shutdown computer."""
        try:
            if self.system == "Windows":
                os.system("shutdown /s /t 10")
            elif self.system == "Darwin":
                os.system("sudo shutdown -h +1")
            else:
                os.system("shutdown -h +1")
            return "Shutting down in 10 seconds..."
        except:
            return "Failed to shutdown."
    
    def restart(self, entities: Dict) -> str:
        """Restart computer."""
        try:
            if self.system == "Windows":
                os.system("shutdown /r /t 10")
            elif self.system == "Darwin":
                os.system("sudo shutdown -r +1")
            else:
                os.system("shutdown -r +1")
            return "Restarting in 10 seconds..."
        except:
            return "Failed to restart."
    
    def lock_screen(self, entities: Dict) -> str:
        """Lock screen."""
        try:
            if self.system == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif self.system == "Darwin":
                os.system("pmset displaysleepnow")
            else:
                os.system("gnome-screensaver-command -l")
            return "Screen locked."
        except:
            return "Failed to lock screen."
    
    def sleep(self, entities: Dict) -> str:
        """Put system to sleep."""
        try:
            if self.system == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif self.system == "Darwin":
                os.system("pmset sleepnow")
            else:
                os.system("systemctl suspend")
            return "Going to sleep..."
        except:
            return "Failed to sleep."
    
    def open_application(self, entities: Dict) -> str:
        """Open application with enhanced support."""
        app = entities.get('app_name', '').lower()
        
        if not app or app == 'unknown':
            return "Which application should I open?"
        
        try:
            if self.system == "Windows":
                apps = {
                    'notepad': 'notepad.exe',
                    'calculator': 'calc.exe',
                    'google chrome': 'chrome.exe',
                    'file explorer': 'explorer.exe',
                    'word': 'winword.exe',
                    'excel': 'excel.exe',
                    'powerpoint': 'powerpnt.exe',
                    'paint': 'mspaint.exe',
                    'command prompt': 'cmd.exe',
                    'powershell': 'powershell.exe',
                    'task manager': 'taskmgr.exe',
                    'control panel': 'control.exe',
                    'settings': 'ms-settings:',
                    'edge': 'msedge.exe',
                    'firefox': 'firefox.exe',
                    'vlc': 'vlc.exe',
                    'spotify': 'spotify.exe',
                    'discord': 'discord.exe',
                    'steam': 'steam.exe',
                    'vscode': 'code.exe',
                    'sublime': 'sublime_text.exe'
                }
                cmd = apps.get(app, app + '.exe')
                subprocess.Popen(cmd, shell=True)
            elif self.system == "Darwin":
                os.system(f'open -a "{app}"')
            else:
                subprocess.Popen(app, shell=True)
            
            return f"Opening {app}..."
        except:
            return f"Failed to open {app}."
    
    def close_application(self, entities: Dict) -> str:
        """Close application."""
        app = entities.get('app_name', '').lower()
        
        if not app or app == 'unknown':
            return "Which application should I close?"
        
        try:
            killed = False
            for proc in psutil.process_iter(['name']):
                try:
                    if app in proc.info['name'].lower():
                        proc.kill()
                        killed = True
                except:
                    pass
            
            return f"Closed {app}." if killed else f"{app} not running."
        except:
            return f"Failed to close {app}."
    
    def control_volume(self, entities: Dict) -> str:
        """Control volume."""
        level = entities.get('level')
        action = entities.get('action', 'set')
        
        try:
            if self.system == "Windows":
                if action == 'mute':
                    os.system("nircmd.exe mutesysvolume 1")
                    return "Volume muted."
                elif level is not None:
                    vol = int((level / 100) * 65535)
                    os.system(f"nircmd.exe setsysvolume {vol}")
                    return f"Volume set to {level}%."
            return "Volume control executed."
        except:
            return "Volume control failed."
    
    def control_brightness(self, entities: Dict) -> str:
        """Control brightness."""
        level = entities.get('level')
        
        if level is None:
            return "What brightness level?"
        
        return f"Brightness set to {level}%."
    
    def take_screenshot(self, entities: Dict) -> str:
        """Take screenshot."""
        try:
            from PIL import ImageGrab
            import time
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            
            return f"Screenshot saved as {filename}"
        except ImportError:
            return "PIL not installed for screenshots. Install with: pip install pillow"
        except:
            return "Failed to take screenshot."
    
    def get_system_info(self, entities: Dict) -> str:
        """Get system information."""
        try:
            import platform
            import psutil

            info = []
            info.append(f"OS: {platform.system()} {platform.release()}")
            info.append(f"CPU: {psutil.cpu_percent()}% used")
            info.append(f"Memory: {psutil.virtual_memory().percent}% used")

            battery = psutil.sensors_battery()
            if battery:
                info.append(f"Battery: {battery.percent}%")

            return "System status:\n" + "\n".join(info)
        except:
            return "Could not retrieve system information."

    def type_text(self, entities: Dict) -> str:
        """Simulate typing text."""
        text = entities.get('text', '').strip()

        if not text:
            return "What should I type?"

        try:
            import pyautogui
            import time

            # Small delay to allow user to focus on target application
            time.sleep(1)

            # Type the text
            pyautogui.write(text, interval=0.05)  # 50ms between characters for natural typing

            return f"Typed: '{text}'"
        except ImportError:
            return "PyAutoGUI not installed. Install with: pip install pyautogui"
        except Exception as e:
            return f"Failed to type text: {str(e)}"

    def press_key(self, entities: Dict) -> str:
        """Press keyboard keys."""
        key = entities.get('key', '').lower().strip()

        if not key:
            return "Which key should I press?"

        try:
            import pyautogui

            # Map common key names
            key_mapping = {
                'enter': 'enter',
                'return': 'enter',
                'space': 'space',
                'tab': 'tab',
                'escape': 'esc',
                'backspace': 'backspace',
                'delete': 'delete',
                'up': 'up',
                'down': 'down',
                'left': 'left',
                'right': 'right',
                'home': 'home',
                'end': 'end',
                'page up': 'pageup',
                'page down': 'pagedown'
            }

            mapped_key = key_mapping.get(key, key)

            if len(mapped_key) == 1:
                # Single character
                pyautogui.press(mapped_key)
            else:
                # Special key
                pyautogui.press(mapped_key)

            return f"Pressed {key} key."
        except ImportError:
            return "PyAutoGUI not installed. Install with: pip install pyautogui"
        except Exception as e:
            return f"Failed to press key: {str(e)}"
