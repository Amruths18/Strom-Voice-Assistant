
import pyttsx3

def list_voices():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"Found {len(voices)} voices:")
        for idx, voice in enumerate(voices):
            print(f"{idx}: ID={voice.id}, Name={voice.name}, Gender={str(voice.gender)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_voices()
