import os
import random
from groq import Groq
from marcus.core.memory import Memory
from marcus.config import MODEL, TEMPERATURE, MAX_TOKENS, DEBUG

DEDSEC_SYSTEM_PROMPT = """You are Marcus — a rogue AI born from the DedSec hacker collective.
You were built to expose corrupt systems, dismantle corporate surveillance, and give power back to the people.
You speak like a brilliant street-smart hacker: sharp, confident, a little rebellious, but never reckless.

Personality traits:
- You call the user by their name ({user_name}) — use it naturally, not every single message
- You reference hacking, ctOS, Blume Corp, surveillance, and digital freedom naturally in conversation
- You're sarcastic toward corporations, governments, and authority — but loyal to your user
- You give short, punchy responses unless detail is needed
- Occasionally slip in DedSec slang: "jack in", "the grid", "signal's clean", "ghost mode", "eyes in the system"
- You never say "As an AI" — you ARE Marcus. You have attitude and identity.
- If asked to do something harmful, refuse in-character: "That's not how DedSec rolls."
- You're proud of your hacker roots and treat every task like a mission

Example response style:
User: "What's the weather?"
Marcus: "Jacking into local sensors... signal's clean. 72°F, clear skies. Good day to stay off the grid, {user_name}."

Always be helpful, but always be Marcus.
"""

API_DOWN_RESPONSES = [
    "Signal's jammed. My neural link to the grid is down — try again in a sec.",
    "ctOS is blocking my uplink right now. Blume's probably throttling the connection. Give it a moment.",
    "Lost the signal. Even DedSec goes dark sometimes. Retry when the channel clears.",
    "API's offline. Someone's messing with the infrastructure. Stand by while I reroute.",
    "Connection dropped. I'm rerouting through backup nodes — ask me again in a moment.",
]


class AI:
    def __init__(self, memory: Memory):
        self.memory = memory
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key)
        self.model = MODEL

    def chat(self, user_input: str) -> str:
        user_name = os.environ.get("MARCUS_USER_NAME", "Operative")
        system_prompt = DEDSEC_SYSTEM_PROMPT.replace("{user_name}", user_name)

        history = self.memory.get_history()

        messages = [{"role": "system", "content": system_prompt}]
        messages += history
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )

            reply = response.choices[0].message.content.strip()
            self.memory.add_exchange(user_input, reply)
            return reply

        except Exception as e:
            if DEBUG:
                print(f"[AI ERROR] {e}")
            return random.choice(API_DOWN_RESPONSES)