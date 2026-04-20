import pyttsx3

engine = pyttsx3.init()

# Optional: adjust voice
engine.setProperty('rate', 180)   # speed
engine.setProperty('volume', 1.0) # volume

def speak(text):
    print(f"Marcus: {text}")
    engine.say(text)
    engine.runAndWait()