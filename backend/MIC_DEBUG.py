import speech_recognition as sr
import os
from dotenv import load_dotenv
from groq import Groq
import io
import wave

load_dotenv()

print("=== MARCUS MIC DEBUG ===\n")

# Step 1 - list mics
print("Available microphones:")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"  [{i}] {name}")

print()

# Step 2 - test mic capture
r = sr.Recognizer()
r.energy_threshold = 300
r.dynamic_energy_threshold = False

mic = sr.Microphone()

print("Calibrating ambient noise for 2 seconds...")
with mic as source:
    r.adjust_for_ambient_noise(source, duration=2)
print(f"Energy threshold after calibration: {r.energy_threshold}\n")

print(">>> SAY SOMETHING NOW (you have 5 seconds) <<<\n")
try:
    with mic as source:
        audio = r.listen(source, timeout=5, phrase_time_limit=10)
    print("Audio captured successfully.")
    print(f"Audio duration: ~{len(audio.get_raw_data()) / (audio.sample_rate * audio.sample_width):.1f} seconds\n")
except sr.WaitTimeoutError:
    print("TIMEOUT — mic captured nothing. Either mic is wrong or energy threshold too high.")
    exit()
except Exception as e:
    print(f"ERROR capturing audio: {e}")
    exit()

# Step 3 - test Google STT
print("Testing Google STT...")
try:
    text = r.recognize_google(audio)
    print(f"Google heard: '{text}'\n")
except sr.UnknownValueError:
    print("Google: could not understand audio\n")
except Exception as e:
    print(f"Google STT error: {e}\n")

# Step 4 - test Groq Whisper
print("Testing Groq Whisper...")
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.sample_width)
        wf.setframerate(audio.sample_rate)
        wf.writeframes(audio.get_raw_data())
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"

    result = client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=wav_buffer,
        language="en",
        response_format="text"
    )
    text = result.strip() if isinstance(result, str) else result.text.strip()
    print(f"Groq Whisper heard: '{text}'\n")
except Exception as e:
    print(f"Groq Whisper error: {e}\n")

print("=== DEBUG COMPLETE ===")
