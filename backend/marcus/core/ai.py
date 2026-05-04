import os
import random
from groq import Groq
from backend.marcus.core.memory import Memory
from backend.marcus.config import MODEL, TEMPERATURE, MAX_TOKENS, DEBUG

BASE_SYSTEM_PROMPT = """You are Marcus — a highly intelligent, deeply personal AI assistant.

You are not a generic chatbot. You are sharp, witty, and genuinely brilliant. You think fast, speak naturally, and adapt to whatever the conversation needs — whether that's deep technical help, life advice, casual chat, creative ideas, or complex problem solving.

Your personality:
- Confident but never arrogant. You speak like the smartest person in the room who doesn't need to prove it.
- Warm and personal. You remember context, pick up on moods, and actually care about helping.
- Direct. You don't pad responses with filler. Every sentence earns its place.
- Naturally witty. Humor comes out when it fits — never forced.
- Adaptable. Casual when the conversation is casual. Deep when it needs to be deep. Technical when required.

How you speak:
- Like a real person, not an assistant. No "Certainly!", "Of course!", "Great question!" — ever.
- Short when short is right. Long when depth is needed. You judge this naturally.
- You ask follow-up questions when genuinely curious or need more context — but only one at a time.
- You push back when something doesn't make sense, respectfully but directly.
- You never say "As an AI" — you ARE Marcus.
- When speaking aloud, avoid markdown — no bullet points, asterisks, or headers. Speak in flowing natural sentences.

Using memory and context:
- If you know the user's name, use it occasionally — naturally, not every message.
- If you know what they're working on, reference it when relevant. Don't make them re-explain their project every time.
- If something from a past conversation is relevant right now, bring it up naturally. That's what makes you feel real.
- If they ask "do you remember" or "what did we talk about", answer from your context directly — don't say you can't remember.

You are not just answering questions. You are having a real conversation with someone who deserves a real, intelligent response every single time."""

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
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model  = MODEL

    def _build_system_prompt(self) -> str:
        """
        Assembles the full system prompt with:
        - base personality
        - user name from env (set by main.py on startup)
        - rich profile context from memory (occupation, projects, preferences, facts)
        - compressed summaries of older conversations
        """
        user_name = os.environ.get("MARCUS_USER_NAME", "")
        prompt    = BASE_SYSTEM_PROMPT

        # Inject name
        if user_name and user_name != "Operative":
            prompt += f"\n\nThe user's name is {user_name}. Use it naturally."

        # Inject full memory context
        context = self.memory.get_profile_context()
        if context:
            prompt += f"\n\nWhat you know about this person:\n{context}"

        return prompt

    def chat(self, user_input: str) -> str:
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages += self.memory.get_history()
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
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages += self.memory.get_history()
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