from dotenv import load_dotenv
import os

load_dotenv()

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

# ==============================
# VOICE SETTINGS (TTS)
# ==============================

TTS_ENABLED = True
TTS_RATE = 175
TTS_VOLUME = 1.0
TTS_VOICE_INDEX = 0


# ==============================
# ASSISTANT IDENTITY
# ==============================

ASSISTANT_NAME = "Marcus"
WAKE_WORD = "hey marcus"


# ==============================
# AI MODEL SETTINGS
# ==============================

MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")  # best on Groq right now
TEMPERATURE = 0.75
MAX_TOKENS = 1024


# ==============================
# MEMORY SETTINGS
# ==============================

MEMORY_ENABLED = True
MAX_HISTORY = 15  # exchanges kept in context


# ==============================
# FILE PATHS
# ==============================

DATA_DIR = "data"
MEMORY_FILE = "data/memory.json"
LOG_FILE = "data/logs/conversation.log"
SHORTCUTS_FILE = "data/shortcuts.json"


# ==============================
# VOICE INPUT SETTINGS
# ==============================

MIC_TIMEOUT = 5
PHRASE_TIME_LIMIT = 10


# ==============================
# DEBUG MODE
# ==============================

DEBUG = True