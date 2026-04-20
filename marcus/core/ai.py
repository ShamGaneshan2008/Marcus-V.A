import os
import requests
from dotenv import load_dotenv
from marcus.core.memory import get_recent_memory

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
You are Marcus, a smart, friendly AI assistant.
You speak naturally like a human and help with tasks.
Keep answers clear and concise.
"""

def ask_ai(prompt):
    memory = get_recent_memory()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for m in memory:
        messages.append({"role": "user", "content": m["user"]})
        messages.append({"role": "assistant", "content": m["ai"]})

    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 500
    }

    response = requests.post(URL, headers=headers, json=data)

    return response.json()["choices"][0]["message"]["content"]