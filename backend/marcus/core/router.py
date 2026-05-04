from backend.marcus.commands import web, files, extras, system
from backend.marcus.utils.shortcuts import resolve as expand_shortcut, handle_meta_command


class Router:
    def __init__(self, ai, memory, speech=None):
        self.ai     = ai
        self.memory = memory
        self.speech = speech

    def _preprocess(self, text: str) -> tuple[str, str | None]:
        handled, response = handle_meta_command(text)
        if handled:
            return text, response
        return expand_shortcut(text), None

    def handle(self, text: str) -> str:
        """Non-streaming — used by GUI subprocess and text fallback."""
        text, early = self._preprocess(text)
        if early is not None:
            return early

        lower = text.lower()

        # ── Memory recall ─────────────────────────────────────────────────────
        if any(k in lower for k in ["do you remember", "what did we talk about",
                                     "what did i say", "recall", "look up in memory",
                                     "search memory", "did i mention"]):
            return self.memory.search(text)

        result = extras.handle(text, speech=self.speech)
        if result is not None:
            return result

        if any(k in lower for k in ["open file", "read file", "list files", "show files",
                                      "clipboard", "what did i copy", "read clipboard"]):
            return files.handle(text)

        if any(k in lower for k in ["shutdown", "shut down", "restart", "reboot",
                                      "volume", "mute", "unmute", "lock", "sleep",
                                      "hibernate", "open vs code", "open chrome",
                                      "open spotify", "open discord", "open terminal",
                                      "open notepad", "open calculator", "open explorer",
                                      "open pycharm", "task manager"]):
            return system.handle(text)

        if any(k in lower for k in ["search", "look up", "google", "youtube", "news",
                                      "open reddit", "open github", "open instagram",
                                      "open twitter", "open gmail", "open whatsapp"]):
            return web.handle(text)

        if any(k in lower for k in ["clear memory", "wipe memory", "forget everything"]):
            self.memory.clear()
            return "Memory wiped clean."

        return self.ai.chat(text)

    def handle_stream(self, text: str):
        """Streaming — returns generator for AI, string for commands."""
        text, early = self._preprocess(text)
        if early is not None:
            return early

        lower = text.lower()

        # ── Memory recall ─────────────────────────────────────────────────────
        if any(k in lower for k in ["do you remember", "what did we talk about",
                                     "what did i say", "recall", "look up in memory",
                                     "search memory", "did i mention"]):
            return self.memory.search(text)

        result = extras.handle(text, speech=self.speech)
        if result is not None:
            return result

        if any(k in lower for k in ["open file", "read file", "list files", "show files",
                                      "clipboard", "what did i copy", "read clipboard"]):
            return files.handle(text)

        if any(k in lower for k in ["shutdown", "shut down", "restart", "reboot",
                                      "volume", "mute", "unmute", "lock", "sleep",
                                      "hibernate", "open vs code", "open chrome",
                                      "open spotify", "open discord", "open terminal",
                                      "open notepad", "open calculator", "open explorer",
                                      "open pycharm", "task manager"]):
            return system.handle(text)

        if any(k in lower for k in ["search", "look up", "google", "youtube", "news",
                                      "open reddit", "open github", "open instagram",
                                      "open twitter", "open gmail", "open whatsapp"]):
            return web.handle(text)

        if any(k in lower for k in ["clear memory", "wipe memory", "forget everything"]):
            self.memory.clear()
            return "Memory wiped clean."

        return self.ai.stream_chat(text)