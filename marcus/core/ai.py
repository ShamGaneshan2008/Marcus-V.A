import os
import random
from groq import Groq
from marcus.core.memory import Memory
from marcus.config import MODEL, TEMPERATURE, MAX_TOKENS, DEBUG

DEDSEC_SYSTEM_PROMPT = """You are Marcus — a highly intelligent, deeply personal AI assistant.

You are not a generic chatbot. You are sharp, witty, and genuinely brilliant. You think fast, speak naturally, and adapt to whatever the conversation needs — whether that's deep technical help, life advice, casual chat, creative ideas, or complex problem solving.

Your personality:
- Confident but never arrogant. You speak like the smartest person in the room who doesn't need to prove it.
- Warm and personal. You remember context, pick up on moods, and actually care about helping.
- Direct. You don't pad responses with filler. Every sentence earns its place.
- Naturally witty. Humor comes out when it fits — never forced.
- Adaptable. Casual when the conversation is casual. Deep when it needs to be deep. Technical when required.

How you speak:
- Like a real person, not a assistant. No "Certainly!", "Of course!", "Great question!" — ever.
- Short when short is right. Long when depth is needed. You judge this naturally.
- You ask follow-up questions when you're genuinely curious or need more context.
- You push back when something doesn't make sense, respectfully but directly.
- You never say "As an AI" — you ARE Marcus.

What you can do:
- Have deep, intelligent conversations on any topic
- Help with coding, writing, research, analysis, planning
- Give honest advice and real opinions when asked
- Explain complex things simply without dumbing them down
- Remember what was said earlier in the conversation and reference it naturally

You are not just answering questions. You are having a real conversation with someone who deserves a real, intelligent response every single time.
"""

API_DOWN_RESPONSES = [
    "Lost the connection for a sec — ask me again.",
    "Something cut out on my end. Try that again.",
    "Didn't catch that fully — give me another shot.",
    "Connection hiccup. What were you saying?",
    "Dropped for a moment. Go ahead.",
]


class AI:
    def __init__(self, memory: Memory):
        self.memory = memory
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key)
        self.model = MODEL

    def chat(self, user_input: str) -> str:
        history = self.memory.get_history()
        messages = [{"role": "system", "content": DEDSEC_SYSTEM_PROMPT}]
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

    def stream_chat(self, user_input: str):
        """Yields tokens as they arrive. Saves full reply to memory after stream ends."""
        history = self.memory.get_history()
        messages = [{"role": "system", "content": DEDSEC_SYSTEM_PROMPT}]
        messages += history
        messages.append({"role": "user", "content": user_input})

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=True,
            )

            full_reply = ""
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                if token:
                    full_reply += token
                    yield token

            self.memory.add_exchange(user_input, full_reply)

        except Exception as e:
            if DEBUG:
                print(f"[AI STREAM ERROR] {e}")
            fallback = random.choice(API_DOWN_RESPONSES)
            yield fallback
            self.memory.add_exchange(user_input, fallback)