import io
import os
import time
import random
import wave
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

WAKE_WORDS = [
    "hey marcus", "hey market", "hey mark", "markus",
    "marcus", "mark", "hey marx", "hey marca"
]

WAKE_RESPONSES = [
    "Yeah, what's up?",
    "I'm here. Go ahead.",
    "Listening.",
    "What do you need?",
    "Talk to me.",
]

MIC_INDEX = 1  # Realtek — your physical mic


class Listener:
    def __init__(self, router, speech):
        self.router = router
        self.speech = speech
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=MIC_INDEX)
        self.is_speaking = False

        self.recognizer.pause_threshold = 0.6
        self.recognizer.non_speaking_duration = 0.4
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = False

        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def _speak_and_wait(self, text):
        self.is_speaking = True
        self.speech.speak(text)
        self.is_speaking = False

    def start_wake_word_loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            # Cap threshold — don't let room noise push it too high
            if self.recognizer.energy_threshold > 600:
                self.recognizer.energy_threshold = 600
            print(f"[MARCUS] Energy threshold: {self.recognizer.energy_threshold:.0f}")

        print("[MARCUS] Ready. Say 'Hey Marcus' to activate.\n")

        while True:
            try:
                audio = self._listen_once(timeout=None, phrase_limit=4)
                if audio is None:
                    continue

                # Skip audio that's too short — background noise clips
                duration = len(audio.get_raw_data()) / (audio.sample_rate * audio.sample_width)
                if duration < 0.5:
                    continue

                text = self._transcribe(audio)
                if text is None:
                    continue

                # Ignore single word/short noise transcriptions in wake word mode
                if len(text.split()) < 2 and not any(w == text.lower().strip() for w in ["marcus", "markus"]):
                    continue

                print(f"[HEARD] {text}")

                if any(w in text.lower() for w in WAKE_WORDS):
                    self._enter_conversation_mode()

            except KeyboardInterrupt:
                print("\n[MARCUS] Shutting down.")
                break
            except Exception as e:
                print(f"[MARCUS] Error: {e}")
                time.sleep(0.5)

    def _enter_conversation_mode(self):
        print("[MARCUS] Activated.\n")
        self._speak_and_wait(random.choice(WAKE_RESPONSES))

        idle_rounds = 0
        max_idle = 3

        while idle_rounds < max_idle:
            print("[MARCUS] Listening...")
            audio = self._listen_once(timeout=7, phrase_limit=20)

            if audio is None:
                idle_rounds += 1
                if idle_rounds == max_idle:
                    self._speak_and_wait("I'll be here when you need me.")
                continue

            # Skip very short audio clips — likely noise
            duration = len(audio.get_raw_data()) / (audio.sample_rate * audio.sample_width)
            if duration < 0.4:
                continue

            text = self._transcribe(audio)
            if not text or len(text.strip()) < 2:
                idle_rounds += 1
                continue

            lower = text.lower()
            print(f"\nYOU    > {text}")

            if any(w in lower for w in ["goodbye", "bye marcus", "go dark", "stop listening", "disconnect"]):
                self._speak_and_wait("Later.")
                print("[MARCUS] Back to wake word mode.\n")
                return

            idle_rounds = 0

            if self.is_speaking:
                self.is_speaking = False
                self.speech.stop()

            response = self.router.handle(text)
            print(f"MARCUS > {response}\n")
            self._speak_and_wait(response)

        print("[MARCUS] Timed out. Back to wake word mode.\n")

    def _listen_once(self, timeout=5, phrase_limit=10):
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
            return audio
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"[MARCUS] Mic error: {e}")
            return None

    def _transcribe(self, audio) -> str | None:
        try:
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(audio.sample_width)
                wf.setframerate(audio.sample_rate)
                wf.writeframes(audio.get_raw_data())
            wav_buffer.seek(0)
            wav_buffer.name = "audio.wav"

            result = self.groq.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=wav_buffer,
                language="en",
                response_format="text"
            )

            text = result.strip() if isinstance(result, str) else result.text.strip()
            return text if text else None

        except Exception as e:
            if os.getenv("DEBUG"):
                print(f"[MARCUS] Whisper error: {e}")
            return self._transcribe_google(audio)

    def _transcribe_google(self, audio) -> str | None:
        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"[MARCUS] Google STT fallback error: {e}")
            return None

    def stop(self):
        try:
            import pygame
            pygame.mixer.music.stop()
        except Exception:
            pass