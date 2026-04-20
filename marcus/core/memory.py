import json
import os

MEMORY_FILE = "data/memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def add_memory(user, ai):
    memory = load_memory()
    memory.append({"user": user, "ai": ai})
    save_memory(memory)

def get_recent_memory(limit=5):
    memory = load_memory()
    return memory[-limit:]