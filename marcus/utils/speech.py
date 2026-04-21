import os
import io
import requests
import pygame
import pyttsx3
from marcus.config import ASSISTANT_NAME, ELEVEN_API_KEY, VOICE_ID


class Speech:
    def __init__(self):
        self.api_key = ELEVEN_API_KEY
        self.voice_id = VOICE_ID or "EXAVITQu4vr4xnSDxMaL"  # free voice fallback

        # 🔥 init pygame once (important)
        pygame.mixer.init()

    def speak(self, text: str):
        # 🔁 If no API → fallback
        if not self.api_key:
            print(f"[{ASSISTANT_NAME}] No ElevenLabs key. Using fallback.")
            self._fallback_tts(text)
            return

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.9
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                # 🔥 NO FILE — play from memory
                audio_stream = io.BytesIO(response.content)

                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()

                # wait until audio finishes
                while pygame.mixer.music.get_busy():
                    continue

            else:
                print(f"[{ASSISTANT_NAME}] ElevenLabs error:", response.text)
                self._fallback_tts(text)

        except Exception as e:
            print(f"[{ASSISTANT_NAME}] TTS error:", e)
            self._fallback_tts(text)

    def _fallback_tts(self, text: str):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 185)   # 🔥 more natural
            engine.setProperty("volume", 1.0)

            engine.say(text)
            engine.runAndWait()

        except Exception as e:
            print(f"[{ASSISTANT_NAME}] Fallback TTS failed:", e)

    def stop(self):
        try:
            import pygame
            pygame.mixer.music.stop()
        except:
            pass