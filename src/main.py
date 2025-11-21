from core.listener import listen
from core.speaker import speak
from features.automation import open_app, take_screenshot

# Main Loop
speak("System Online")
while True:
    command = listen()
    
    if "notepad" in command:
        open_app("notepad")
        speak("Opening Notepad")
    elif "screenshot" in command:
        take_screenshot()
        speak("Screenshot saved")