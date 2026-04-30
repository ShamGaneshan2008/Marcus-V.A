import os
import io
import asyncio
import tempfile

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
import requests

from marcus.config import (
    ASSISTANT_NAME, ELEVEN_API_KEY, VOICE_ID,
    TTS_RATE, TTS_VOLUME, DEBUG
)


class Speech:
    def __init__(self):
        self.api_key = ELEVEN_API_KEY
        self.voice_id = VOICE_ID or "pNInz6obpgDQGcFmaJgB"
        pygame.mixer.init()
        self._edge_voice = "en-US-GuyNeural"  # natural male voice

    def speak(self, text: str):
        if not text.strip():
            return

        if self.api_key:
            success = self._elevenlabs(text)
            if success:
                return

        # fallback to edge-tts
        self._edge_tts(text)

    def speak_chunked(self, text: str):
        self.speak(text)

    def _elevenlabs(self, text: str) -> bool:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.85,
                "style": 0.3,
                "use_speaker_boost": True
            }
        }
        try:
            response = requests.post(url, json=data, headers=headers, timeout=15)
            if response.status_code == 200:
                audio_stream = io.BytesIO(response.content)
                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                return True
            else:
                if DEBUG:
                    print(f"[{ASSISTANT_NAME}] ElevenLabs error {response.status_code}:", response.text[:100])
                return False
        except requests.exceptions.Timeout:
            if DEBUG:
                print(f"[{ASSISTANT_NAME}] ElevenLabs timed out.")
            return False
        except Exception as e:
            if DEBUG:
                print(f"[{ASSISTANT_NAME}] ElevenLabs error: {e}")
            return False

    def _edge_tts(self, text: str):
        """Microsoft neural TTS via edge-tts — free, sounds natural."""
        try:
            import edge_tts

            async def _speak():
                communicate = edge_tts.Communicate(text, self._edge_voice)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tmp_path = f.name
                await communicate.save(tmp_path)
                return tmp_path

            tmp_path = asyncio.run(_speak())
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            os.unlink(tmp_path)

        except ImportError:
            print(f"[{ASSISTANT_NAME}] edge-tts not installed. Run: pip install edge-tts")
            self._pyttsx3_fallback(text)
        except Exception as e:
            if DEBUG:
                print(f"[{ASSISTANT_NAME}] edge-tts error: {e}")
            self._pyttsx3_fallback(text)

    def _pyttsx3_fallback(self, text: str):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", TTS_RATE)
            engine.setProperty("volume", TTS_VOLUME)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[{ASSISTANT_NAME}] All TTS failed: {e}")

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass