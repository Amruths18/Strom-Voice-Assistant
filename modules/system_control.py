"""
System Control Module for Strom AI Assistant
Handles system-level operations: shutdown, restart, lock, application management,
volume and brightness control.
"""

import os
import platform
import subprocess
import psutil
from typing import Dict, Optional


class SystemControl:
    """
    Manages system-level control operations.
    Platform-aware implementation for Windows, macOS, and Linux.
    """
    
    def __init__(self):
        """Initialize system control module."""
        self.system = platform.system()
        print(f"[SystemControl] Initialized for {self.system}")
    
    def shutdown(self, entities: Dict) -> str:
        """
        Shutdown the computer.
        
        Args:
            entities: Command entities (unused)
            
        Returns:
            Status message
        """
        try:
            if self.system == "Windows":
                os.system("shutdown /s /t 5")
            elif self.system == "Darwin":  # macOS
                os.system("sudo shutdown -h now")
            else:  # Linux
                os.system("shutdown -h now")
            
            return "Shutting down the system in 5 seconds..."
        except Exception as e:
            return f"Failed to shutdown: {str(e)}"
    
    def restart(self, entities: Dict) -> str:
        """
        Restart the computer.
        
        Args:
            entities: Command entities (unused)
            
        Returns:
            Status message
        """
        try:
            if self.system == "Windows":
                os.system("shutdown /r /t 5")
            elif self.system == "Darwin":
                os.system("sudo shutdown -r now")
            else:
                os.system("shutdown -r now")
            
            return "Restarting the system in 5 seconds..."
        except Exception as e:
            return f"Failed to restart: {str(e)}"
    
    def lock_screen(self, entities: Dict) -> str:
        """
        Lock the computer screen.
        
        Args:
            entities: Command entities (unused)
            
        Returns:
            Status message
        """
        try:
            if self.system == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
            elif self.system == "Darwin":
                os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
            else:
                os.system("gnome-screensaver-command -l")
            
            return "Screen locked."
        except Exception as e:
            return f"Failed to lock screen: {str(e)}"
    
    def sleep(self, entities: Dict) -> str:
        """
        Put computer to sleep.
        
        Args:
            entities: Command entities (unused)
            
        Returns:
            Status message
        """
        try:
            if self.system == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif self.system == "Darwin":
                os.system("pmset sleepnow")
            else:
                os.system("systemctl suspend")
            
            return "Putting system to sleep..."
        except Exception as e:
            return f"Failed to sleep: {str(e)}"
    
    def open_application(self, entities: Dict) -> str:
        """
        Open an application.
        
        Args:
            entities: Must contain 'app_name'
            
        Returns:
            Status message
        """
        app_name = entities.get('app_name', '').lower()
        
        if not app_name or app_name == 'unknown':
            return "Please specify which application to open."
        
        try:
            if self.system == "Windows":
                # Common Windows applications
                app_paths = {
                    'notepad': 'notepad.exe',
                    'calculator': 'calc.exe',
                    'google chrome': 'chrome.exe',
                    'file explorer': 'explorer.exe',
                    'microsoft word': 'winword.exe',
                    'microsoft excel': 'excel.exe',
                    'visual studio code': 'code.exe'
                }
                
                app_cmd = app_paths.get(app_name, app_name + '.exe')
                subprocess.Popen(app_cmd, shell=True)
                
            elif self.system == "Darwin":
                # macOS applications
                app_paths = {
                    'google chrome': '/Applications/Google Chrome.app',
                    'safari': '/Applications/Safari.app',
                    'finder': '/System/Library/CoreServices/Finder.app',
                    'calculator': '/Applications/Calculator.app'
                }
                
                app_path = app_paths.get(app_name, f'/Applications/{app_name.title()}.app')
                os.system(f'open "{app_path}"')
                
            else:  # Linux
                subprocess.Popen(app_name, shell=True)
            
            return f"Opening {app_name}..."
            
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"
    
    def close_application(self, entities: Dict) -> str:
        """
        Close a running application.
        
        Args:
            entities: Must contain 'app_name'
            
        Returns:
            Status message
        """
        app_name = entities.get('app_name', '').lower()
        
        if not app_name or app_name == 'unknown':
            return "Please specify which application to close."
        
        try:
            # Find and kill process
            killed = False
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name in proc_name:
                        proc.kill()
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed:
                return f"Closed {app_name}."
            else:
                return f"{app_name} is not currently running."
                
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"
    
    def control_volume(self, entities: Dict) -> str:
        """
        Control system volume.
        
        Args:
            entities: May contain 'level' (0-100) and 'action' (increase/decrease/set/mute)
            
        Returns:
            Status message
        """
        action = entities.get('action', 'set')
        level = entities.get('level')
        
        try:
            if self.system == "Windows":
                if action == 'mute':
                    os.system("nircmd.exe mutesysvolume 1")
                    return "Volume muted."
                elif action == 'unmute':
                    os.system("nircmd.exe mutesysvolume 0")
                    return "Volume unmuted."
                elif level is not None:
                    # NirCmd sets volume from 0-65535
                    vol_value = int((level / 100) * 65535)
                    os.system(f"nircmd.exe setsysvolume {vol_value}")
                    return f"Volume set to {level}%."
                elif action == 'increase':
                    os.system("nircmd.exe changesysvolume 2000")
                    return "Volume increased."
                elif action == 'decrease':
                    os.system("nircmd.exe changesysvolume -2000")
                    return "Volume decreased."
            
            elif self.system == "Darwin":
                if action == 'mute':
                    os.system("osascript -e 'set volume output muted true'")
                    return "Volume muted."
                elif action == 'unmute':
                    os.system("osascript -e 'set volume output muted false'")
                    return "Volume unmuted."
                elif level is not None:
                    os.system(f"osascript -e 'set volume output volume {level}'")
                    return f"Volume set to {level}%."
            
            else:  # Linux (using amixer)
                if action == 'mute':
                    os.system("amixer set Master mute")
                    return "Volume muted."
                elif action == 'unmute':
                    os.system("amixer set Master unmute")
                    return "Volume unmuted."
                elif level is not None:
                    os.system(f"amixer set Master {level}%")
                    return f"Volume set to {level}%."
            
            return "Volume control command received."
            
        except Exception as e:
            return f"Failed to control volume: {str(e)}"
    
    def control_brightness(self, entities: Dict) -> str:
        """
        Control screen brightness.
        
        Args:
            entities: May contain 'level' (0-100) and 'action' (increase/decrease/set)
            
        Returns:
            Status message
        """
        action = entities.get('action', 'set')
        level = entities.get('level')
        
        try:
            if self.system == "Windows":
                if level is not None:
                    os.system(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})")
                    return f"Brightness set to {level}%."
                else:
                    return "Please specify brightness level."
            
            elif self.system == "Darwin":
                if level is not None:
                    # macOS brightness control (requires brightness utility)
                    brightness_val = level / 100
                    os.system(f"brightness {brightness_val}")
                    return f"Brightness set to {level}%."
            
            else:  # Linux
                if level is not None:
                    brightness_val = int((level / 100) * 255)
                    os.system(f"echo {brightness_val} > /sys/class/backlight/intel_backlight/brightness")
                    return f"Brightness set to {level}%."
            
            return "Brightness control may require additional permissions."
            
        except Exception as e:
            return f"Failed to control brightness: {str(e)}"


# Test function
def _test_system_control():
    """Test system control module."""
    
    print("=== Strom System Control Test ===\n")
    
    sys_control = SystemControl()
    
    # Test opening application
    print("Test: Open Calculator")
    result = sys_control.open_application({'app_name': 'calculator'})
    print(f"Result: {result}\n")
    
    # Test volume control
    print("Test: Set volume to 50%")
    result = sys_control.control_volume({'action': 'set', 'level': 50})
    print(f"Result: {result}\n")


if __name__ == "__main__":
    _test_system_control()