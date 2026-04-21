import speech_recognition as sr
import threading
import time
import re

WAKE_WORD = "hey marcus"


class Listener:
    def __init__(self, router, speech):
        self.router = router
        self.speech = speech
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_active = False
        self.is_speaking = False

        # 🔥 tuning
        self.recognizer.pause_threshold = 0.6
        self.recognizer.energy_threshold = 150
        self.recognizer.dynamic_energy_threshold = True

    # 🔥 FAST SPEECH FUNCTION
    def _speak_fast(self, text):
        import re

        self.is_speaking = True

        chunks = re.split(r'(?<=[.!?]) +', text)

        for chunk in chunks:
            if not self.is_speaking:
                break
            if chunk.strip():
                self.speech.speak(chunk)

        self.is_speaking = False

    def start_wake_word_loop(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[MARCUS] Ambient noise calibrated. Listening for wake word...")

        while True:
            try:
                audio = self._listen_once(timeout=None, phrase_limit=4)
                if audio is None:
                    continue

                text = self._transcribe(audio)
                if text is None:
                    continue

                if WAKE_WORD in text.lower():
                    if any(word in text.lower() for word in [
                        "marcus", "hey marcus", "hey market", "marcusss", "markus"
                    ]):
                        self._enter_conversation_mode()

            except KeyboardInterrupt:
                print("\n[MARCUS] Signal lost. DedSec out.")
                break
            except Exception as e:
                print(f"[MARCUS] Listener error: {e}")
                time.sleep(1)

    def _enter_conversation_mode(self):
        # 🔥 start speaking (non-blocking)
        threading.Thread(
            target=self._speak_fast,
            args=("Signal acquired. What's the mission?",),
            daemon=True
        ).start()

        print("[MARCUS] Wake word detected — entering conversation mode.")

        idle_rounds = 0
        max_idle = 3

        while idle_rounds < max_idle:
            audio = self._listen_once(timeout=6, phrase_limit=15)

            # 🔥 INTERRUPT HERE
            if self.is_speaking:
                print("[MARCUS] Interrupted.")
                self.is_speaking = False
                self.speech.stop()

            if audio is None:
                idle_rounds += 1
                print(f"[MARCUS] Idle {idle_rounds}/{max_idle}...")
                continue

            text = self._transcribe(audio)
            if text is None:
                idle_rounds += 1
                continue

            if any(word in text.lower() for word in ["goodbye", "bye marcus", "go dark", "disconnect"]):
                threading.Thread(
                    target=self._speak_fast,
                    args=("Going dark. DedSec out.",),
                    daemon=True
                ).start()

                print("[MARCUS] Session ended. Back to wake word mode.")
                return

            idle_rounds = 0
            print(f"[YOU] {text}")

            # 🔥 interrupt BEFORE new response
            if self.is_speaking:
                self.is_speaking = False
                self.speech.stop()

            response = self.router.handle(text)
            print(f"[MARCUS] {response}")

            threading.Thread(
                target=self._speak_fast,
                args=(response,),
                daemon=True
            ).start()

        print("[MARCUS] Session timed out. Back to listening for wake word.")

        threading.Thread(
            target=self._speak_fast,
            args=("Going quiet. Call me when you need me.",),
            daemon=True
        ).start()

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
            text = self.recognizer.recognize_google(audio)
            print("HEARD:", text)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[MARCUS] STT service error: {e}")
            return None

    def stop(self):
        try:
            import pygame
            pygame.mixer.music.stop()
        except:
            pass