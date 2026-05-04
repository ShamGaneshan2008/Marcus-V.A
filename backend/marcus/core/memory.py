import os
import re
import json
from datetime import datetime

MEMORY_FILE  = os.path.join(os.path.dirname(__file__), "../../data/memory.json")
PROFILE_FILE = os.path.join(os.path.dirname(__file__), "../../data/profile.json")
SUMMARY_FILE = os.path.join(os.path.dirname(__file__), "../../data/summary.json")
LOG_FILE     = os.path.join(os.path.dirname(__file__), "../../data/logs/conversation.log")

# How many recent exchanges to keep verbatim before summarising older ones
RECENT_WINDOW = 10


class Memory:
    def __init__(self):
        self.history  = []   # recent exchanges (role/content dicts)
        self.profile  = {}   # persistent facts about the user
        self.summary  = []   # compressed summaries of older conversations
        self._ensure_files()
        self._load_all()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _ensure_files(self):
        for path in [MEMORY_FILE, PROFILE_FILE, SUMMARY_FILE, LOG_FILE]:
            os.makedirs(os.path.dirname(path), exist_ok=True)

        defaults = {
            MEMORY_FILE:  [],
            PROFILE_FILE: {},
            SUMMARY_FILE: [],
        }
        for path, default in defaults.items():
            if not os.path.exists(path):
                with open(path, "w") as f:
                    json.dump(default, f)

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                f.write(f"=== Marcus V.A Log ===\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def _load_all(self):
        # history
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
            self.history = data.get("events", data) if isinstance(data, dict) else data
        except Exception:
            self.history = []

        # profile
        try:
            with open(PROFILE_FILE, "r") as f:
                self.profile = json.load(f)
        except Exception:
            self.profile = {}

        # summaries
        try:
            with open(SUMMARY_FILE, "r") as f:
                self.summary = json.load(f)
        except Exception:
            self.summary = []

    # ── History ───────────────────────────────────────────────────────────────

    def get_history(self) -> list:
        """Return the most recent exchanges for the API messages array."""
        return self.history[-(RECENT_WINDOW * 2):]

    def add_exchange(self, user_input: str, ai_reply: str):
        self.history.append({"role": "user",      "content": user_input})
        self.history.append({"role": "assistant",  "content": ai_reply})

        self._extract_facts(user_input, ai_reply)
        self._maybe_compress()
        self._persist_history()
        self._write_log(user_input, ai_reply)

    def _persist_history(self):
        try:
            with open(MEMORY_FILE, "w") as f:
                json.dump(self.history[-200:], f, indent=2)
        except Exception as e:
            print(f"[MARCUS] Memory write error: {e}")

    # ── Compression / summarisation ───────────────────────────────────────────
    # When history grows beyond RECENT_WINDOW * 2 pairs, compress the oldest
    # exchanges into a plain-English summary bullet and drop the raw pairs.
    # This means Marcus never loses context — he just holds it more efficiently.

    def _maybe_compress(self):
        max_raw = RECENT_WINDOW * 2 * 2   # pairs × 2 messages each
        if len(self.history) <= max_raw:
            return

        # Take the oldest half for compression
        cut       = len(self.history) // 2
        old_pairs = self.history[:cut]
        self.history = self.history[cut:]

        summary_text = self._summarise_pairs(old_pairs)
        if summary_text:
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "summary":   summary_text,
            }
            self.summary.append(entry)
            # keep only last 20 summaries
            self.summary = self.summary[-20:]
            try:
                with open(SUMMARY_FILE, "w") as f:
                    json.dump(self.summary, f, indent=2)
            except Exception as e:
                print(f"[MARCUS] Summary write error: {e}")

    def _summarise_pairs(self, pairs: list) -> str:
        """Convert raw exchange pairs into a compact plain-English summary."""
        lines = []
        for msg in pairs:
            role    = "User" if msg["role"] == "user" else "Marcus"
            content = msg["content"].strip()
            if content:
                lines.append(f"{role}: {content}")
        if not lines:
            return ""
        # Simple extractive summary — take first sentence of each turn
        bullets = []
        for line in lines:
            first_sentence = re.split(r'(?<=[.!?])\s', line)[0]
            if len(first_sentence) > 10:
                bullets.append(f"- {first_sentence}")
        return "\n".join(bullets[:12])   # cap at 12 bullets per summary

    # ── Profile / fact extraction ─────────────────────────────────────────────
    # Passively reads every exchange and pulls out durable facts.
    # These persist across sessions and get injected into the system prompt.

    def get_profile_context(self) -> str:
        """
        Builds a rich context string for the AI system prompt.
        Covers: name, occupation, projects, preferences, notes, and
        compressed summaries of older conversations.
        """
        parts = []

        if self.profile.get("name"):
            parts.append(f"User's name: {self.profile['name']}.")

        if self.profile.get("occupation"):
            parts.append(f"Occupation: {self.profile['occupation']}.")

        if self.profile.get("projects"):
            recent_projects = self.profile["projects"][-3:]
            parts.append(f"Currently working on: {', '.join(recent_projects)}.")

        if self.profile.get("interests"):
            parts.append(f"Interests: {', '.join(self.profile['interests'][-5:])}.")

        if self.profile.get("preferences"):
            parts.append(f"Preferences: {', '.join(self.profile['preferences'][-5:])}.")

        if self.profile.get("facts"):
            parts.append(f"Known facts: {'; '.join(self.profile['facts'][-5:])}.")

        if self.profile.get("notes"):
            parts.append(f"Notes: {'; '.join(self.profile['notes'][-3:])}.")

        # Append compressed summaries of older conversations
        if self.summary:
            recent_summaries = self.summary[-3:]
            summary_block = "\n".join(s["summary"] for s in recent_summaries)
            parts.append(f"\nPast conversation context:\n{summary_block}")

        return "\n".join(parts)

    def _extract_facts(self, user_input: str, ai_reply: str):
        """
        Rule-based fact extraction from every exchange.
        Covers: name, occupation, projects, preferences, facts, interests.
        """
        lower = user_input.lower().strip()

        # ── Name ──────────────────────────────────────────────────────────────
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"call me (\w+)",
            r"i am (\w+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, lower)
            if match:
                name = match.group(1).capitalize()
                STOPWORDS = {"a", "an", "the", "here", "going", "trying", "just",
                             "not", "so", "now", "actually", "really", "good", "fine"}
                if name.lower() not in STOPWORDS and len(name) > 1:
                    self._set("name", name)
                break

        # ── Occupation ────────────────────────────────────────────────────────
        occ_patterns = [
            r"i(?:'m| am) (?:a |an )?(\w+ (?:developer|engineer|designer|student|"
            r"doctor|teacher|researcher|manager|analyst|writer|artist|founder|cto|ceo))",
            r"i work as (?:a |an )?(.+?)(?:\.|,|$)",
            r"i(?:'m| am) studying (.+?)(?:\.|,|$)",
        ]
        for pattern in occ_patterns:
            match = re.search(pattern, lower)
            if match:
                self._set("occupation", match.group(1).strip().title())
                break

        # ── Projects ──────────────────────────────────────────────────────────
        project_patterns = [
            r"(?:working on|building|making|developing|coding|created?) (?:a |an |my )?(.+?)(?:\.|,|$)",
            r"my (?:project|app|bot|tool|website|system) (?:is called |is |called )?[\"']?(.+?)[\"']?(?:\.|,|$)",
        ]
        for pattern in project_patterns:
            match = re.search(pattern, lower)
            if match:
                project = match.group(1).strip()
                if 3 < len(project) < 60:
                    self._append("projects", project.title())
                break

        # ── Preferences ───────────────────────────────────────────────────────
        pref_patterns = [
            r"i (?:prefer|like|love|enjoy|use|always use) (.+?)(?:\.|,|$)",
            r"my (?:favourite|favorite) (.+?) is (.+?)(?:\.|,|$)",
        ]
        for pattern in pref_patterns:
            match = re.search(pattern, lower)
            if match:
                pref = match.group(0).strip()
                if 5 < len(pref) < 80:
                    self._append("preferences", pref)
                break

        # ── Interests ─────────────────────────────────────────────────────────
        interest_kws = ["into", "obsessed with", "passionate about", "fascinated by",
                        "learning about", "studying", "researching"]
        for kw in interest_kws:
            if kw in lower:
                idx   = lower.index(kw) + len(kw)
                chunk = lower[idx:idx + 50].strip().split(".")[0].split(",")[0].strip()
                if 3 < len(chunk) < 50:
                    self._append("interests", chunk)
                break

        # ── Explicit facts ("remember that...", "note that...") ───────────────
        fact_patterns = [
            r"remember (?:that )?(.+?)(?:\.|,|$)",
            r"note (?:that )?(.+?)(?:\.|,|$)",
            r"don't forget (?:that )?(.+?)(?:\.|,|$)",
            r"keep in mind (?:that )?(.+?)(?:\.|,|$)",
        ]
        for pattern in fact_patterns:
            match = re.search(pattern, lower)
            if match:
                fact = match.group(1).strip()
                if 5 < len(fact) < 120:
                    self._append("facts", fact)
                break

    def _set(self, key: str, value):
        if self.profile.get(key) != value:
            self.profile[key] = value
            self._save_profile()
            print(f"[MARCUS] Learned {key}: {value}")

    def _append(self, key: str, value: str):
        if key not in self.profile:
            self.profile[key] = []
        if value not in self.profile[key]:
            self.profile[key].append(value)
            self.profile[key] = self.profile[key][-20:]   # cap list size
            self._save_profile()

    def update_profile(self, key: str, value):
        """External API for direct profile updates (e.g. from main.py name prompt)."""
        if key in ("preferences", "notes", "facts", "projects", "interests"):
            self._append(key, value)
        else:
            self._set(key, value)

    def _save_profile(self):
        try:
            with open(PROFILE_FILE, "w") as f:
                json.dump(self.profile, f, indent=2)
        except Exception as e:
            print(f"[MARCUS] Profile save error: {e}")

    # ── Recall ────────────────────────────────────────────────────────────────

    def search(self, query: str) -> str:
        """
        Simple keyword search across history and summaries.
        Called by router when user asks "what did we talk about" / "do you remember".
        Returns a plain-English result string.
        """
        query_lower = query.lower()
        hits = []

        # search recent history
        for msg in reversed(self.history):
            if query_lower in msg["content"].lower():
                role = "You" if msg["role"] == "user" else "Marcus"
                hits.append(f"{role}: {msg['content'][:120]}")
            if len(hits) >= 3:
                break

        # search summaries if not enough hits
        if len(hits) < 2:
            for entry in reversed(self.summary):
                if query_lower in entry["summary"].lower():
                    hits.append(f"[Earlier — {entry['timestamp']}]: {entry['summary'][:200]}")
                if len(hits) >= 3:
                    break

        if hits:
            return "Here's what I found:\n" + "\n".join(hits)
        return "I don't have anything on that in memory."

    # ── Log / clear ───────────────────────────────────────────────────────────

    def _write_log(self, user_input: str, ai_reply: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(
                    f"[{timestamp}]\n"
                    f"  YOU    : {user_input}\n"
                    f"  MARCUS : {ai_reply}\n"
                    f"{'─' * 60}\n"
                )
        except Exception as e:
            print(f"[MARCUS] Log write error: {e}")

    def clear(self):
        self.history = []
        self.summary = []
        with open(MEMORY_FILE,  "w") as f: json.dump([], f)
        with open(SUMMARY_FILE, "w") as f: json.dump([], f)
        print("[MARCUS] Memory wiped.")