import os
import re
import io
import requests
import pygame
import pyttsx3
from marcus.config import ASSISTANT_NAME, ELEVEN_API_KEY, VOICE_ID, TTS_RATE, TTS_VOLUME


class Speech:
    def __init__(self):
        self.api_key = ELEVEN_API_KEY
        self.voice_id = VOICE_ID or "EXAVITQu4vr4xnSDxMaL"

        pygame.mixer.init()

        # init once — reinitialising on every call causes issues on Windows
        self._tts_engine = None
        try:
            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty("rate", TTS_RATE)
            self._tts_engine.setProperty("volume", TTS_VOLUME)
        except Exception as e:
            print(f"[{ASSISTANT_NAME}] pyttsx3 init failed: {e}")

    def speak(self, text: str):
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
                audio_stream = io.BytesIO(response.content)
                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
            else:
                print(f"[{ASSISTANT_NAME}] ElevenLabs error:", response.text)
                self._fallback_tts(text)

        except Exception as e:
            print(f"[{ASSISTANT_NAME}] TTS error:", e)
            self._fallback_tts(text)

    def speak_chunked(self, text: str):
        """Split on sentence boundaries and speak chunk by chunk."""
        chunks = re.split(r'(?<=[.!?]) +', text)
        for chunk in chunks:
            if chunk.strip():
                self.speak(chunk)

    def _fallback_tts(self, text: str):
        if self._tts_engine is None:
            print(f"[{ASSISTANT_NAME}] No TTS engine available.")
            return
        try:
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
        except Exception as e:
            print(f"[{ASSISTANT_NAME}] Fallback TTS failed:", e)

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass