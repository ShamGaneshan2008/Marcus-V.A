import os
import re
import sys
import json
import threading
from dotenv import load_dotenv
from marcus.core.ai import AI
from marcus.core.router import Router
from marcus.core.memory import Memory
from marcus.utils.speech import Speech

load_dotenv()

# ── Name memory helpers ──────────────────────────────────────────────────────
# memory.json can be [] (legacy) or {"user_name": "...", "events": [...]}.
# These two functions handle both shapes transparently.

MEMORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marcus/memory.json")

def _load_raw() -> dict:
    """Return memory as a dict, upgrading the legacy [] format if needed."""
    try:
        with open(MEMORY_PATH, "r") as f:
            data = json.load(f)
        if isinstance(data, list):          # legacy format — migrate in place
            data = {"user_name": None, "events": data}
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"user_name": None, "events": []}

def _save_raw(data: dict):
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_user_name() -> str | None:
    return _load_raw().get("user_name")

def set_user_name(name: str):
    data = _load_raw()
    data["user_name"] = name.strip().title()
    _save_raw(data)

def resolve_user_name(interactive: bool = True) -> str:
    """
    Return the stored name.  If none exists and interactive=True, ask once
    and persist it.  Falls back to 'Operative' so callers never get None.
    """
    name = get_user_name()
    if name:
        return name
    if not interactive:
        return "Operative"
    print("[MARCUS] I don't have your name on file.")
    raw = input("[MARCUS] What should I call you? > ").strip()
    if raw:
        set_user_name(raw)
        name = raw.title()
        print(f"[MARCUS] Got it. Good to meet you, {name}.\n")
        return name
    return "Operative"

# ── Patch router so every response can include the user's name ───────────────
# We wrap router.handle() to inject the name into the system context via a
# simple env var.  Your AI/router can then read os.environ["MARCUS_USER_NAME"]
# and address the user by name in its system prompt.

def _patch_router_env(name: str):
    os.environ["MARCUS_USER_NAME"] = name


# ── Entry points ─────────────────────────────────────────────────────────────

def main():
    print("""
    ███╗   ███╗ █████╗ ██████╗  ██████╗██╗   ██╗███████╗
    ████╗ ████║██╔══██╗██╔══██╗██╔════╝██║   ██║██╔════╝
    ██╔████╔██║███████║██████╔╝██║     ██║   ██║███████╗
    ██║╚██╔╝██║██╔══██║██╔══██╗██║     ██║   ██║╚════██║
    ██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╗╚██████╔╝███████║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
         V.A — DedSec Intelligence Layer | by Marcus
    """)

    user_name = resolve_user_name(interactive=True)
    _patch_router_env(user_name)

    memory = Memory()
    ai = AI(memory)
    speech = Speech()
    router = Router(ai, memory, speech=speech)

    mic_available = False
    try:
        import speech_recognition as sr
        test_mic = sr.Microphone()
        with test_mic as source:
            pass
        mic_available = True
    except Exception as e:
        print(f"[MARCUS] Mic check failed: {e}")

    if mic_available:
        from marcus.utils.listener import Listener
        listener = Listener(router, speech)
        print(f"[MARCUS] ctOS link established. Say 'Hey Marcus' to activate, {user_name}.\n")
        listener.start_wake_word_loop()
    else:
        print(f"[MARCUS] No mic detected. Dropping into text input mode.")
        _text_fallback_loop(router, speech, user_name)


def _text_fallback_loop(router, speech, user_name: str = "Operative"):
    print(f"[MARCUS] Text mode active. Type your command, {user_name}. ('quit' to exit)\n")

    while True:
        try:
            user_input = input("YOU    > ").strip()

            if not user_input:
                continue

            # Allow user to update their name mid-session
            if user_input.lower().startswith("my name is "):
                new_name = user_input[11:].strip().title()
                set_user_name(new_name)
                _patch_router_env(new_name)
                user_name = new_name
                print(f"[MARCUS] Updated. I'll call you {new_name} from now on.\n")
                continue

            if user_input.lower() in ("quit", "exit", "go dark", "bye", "goodbye"):
                print(f"[MARCUS] Going dark. DedSec out, {user_name}.")
                break

            response = router.handle(user_input)
            print(f"MARCUS > {response}\n")

            threading.Thread(
                target=speech.speak_chunked,
                args=(response,),
                daemon=True
            ).start()

        except (KeyboardInterrupt, EOFError):
            print("\n[MARCUS] Signal lost. DedSec out.")
            break


if __name__ == "__main__":
    # GUI passes --cmd "user input" to get a single response and exit.
    # Name is read from memory.json — no interactive prompt in this path.
    if "--cmd" in sys.argv:
        idx = sys.argv.index("--cmd")
        if idx + 1 < len(sys.argv):
            cmd = sys.argv[idx + 1]
            load_dotenv()
            user_name = resolve_user_name(interactive=False)
            _patch_router_env(user_name)
            memory = Memory()
            ai = AI(memory)
            speech = Speech()
            router = Router(ai, memory, speech=speech)
            print(router.handle(cmd))
        else:
            print("[ERROR] --cmd flag provided but no command given.")
    else:
        main()