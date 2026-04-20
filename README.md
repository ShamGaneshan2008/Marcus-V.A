# 🤖 Marcus — AI Voice Assistant

> A modular, conversational AI voice assistant built with Python — capable of listening, thinking, and speaking back.

---

## 📁 Project Structure

```
Marcus_V.A/
├── data/
│   └── memory.json          # Persistent memory store for conversation context
├── marcus/
│   ├── commands/            # Executable command modules
│   │   ├── files.py         # File system operations
│   │   ├── system.py        # System-level commands (shutdown, volume, etc.)
│   │   └── web.py           # Web search and browsing actions
│   ├── core/                # Core assistant logic
│   │   ├── ai.py            # AI inference and response generation
│   │   ├── memory.py        # Memory read/write and context management
│   │   └── router.py        # Intent routing — directs input to the right command
│   └── utils/               # Utility helpers
│       ├── listener.py      # Microphone input and speech-to-text
│       └── speech.py        # Text-to-speech output
├── main.py                  # Application entry point
├── run.py                   # Convenience launcher script
├── .env                     # Environment variables (API keys, config)
└── requirements.txt         # Python dependencies
```

---

## ✨ Features

- 🎙️ **Voice Input** — Listens via microphone using real-time speech recognition
- 🧠 **AI-Powered Responses** — Generates intelligent replies through a configurable AI backend
- 🔊 **Text-to-Speech Output** — Speaks responses back naturally
- 🗂️ **File Commands** — Perform file system operations by voice
- 🌐 **Web Integration** — Search the web or open URLs hands-free
- 💻 **System Control** — Execute system-level actions via voice
- 💾 **Persistent Memory** — Retains context across sessions via `memory.json`
- 🔀 **Intent Router** — Cleanly routes commands to the appropriate module

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A working microphone
- API key for your chosen AI backend (e.g. OpenAI, Anthropic)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Marcus_V.A.git
cd Marcus_V.A

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Running Marcus

```bash
# Option A — via run.py launcher
python run.py

# Option B — directly
python main.py
```

---

## ⚙️ Configuration

All configuration is handled through the `.env` file:

```env
AI_API_KEY=your_api_key_here
AI_MODEL=gpt-4o              # or any supported model
VOICE_LANGUAGE=en-US
SPEECH_RATE=175
MEMORY_PATH=data/memory.json
```

---

## 🧩 Module Overview

| Module | File | Responsibility |
|---|---|---|
| **Listener** | `utils/listener.py` | Captures microphone input, converts speech to text |
| **Speech** | `utils/speech.py` | Converts text responses to spoken audio output |
| **AI Core** | `core/ai.py` | Sends prompts to the AI backend, returns responses |
| **Memory** | `core/memory.py` | Loads and saves conversation history to `memory.json` |
| **Router** | `core/router.py` | Parses intent and dispatches to the correct command |
| **Files** | `commands/files.py` | Handles file open, read, search, and management |
| **System** | `commands/system.py` | Executes OS-level actions (volume, shutdown, apps) |
| **Web** | `commands/web.py` | Performs web searches and opens URLs in the browser |

---

## 📦 Dependencies

Install all dependencies with:

```bash
pip install -r requirements.txt
```

Key libraries used (add yours as applicable):

| Library | Purpose |
|---|---|
| `speechrecognition` | Microphone input & STT |
| `pyttsx3` / `gTTS` | Text-to-speech |
| `openai` / `anthropic` | AI backend |
| `python-dotenv` | Environment variable management |
| `pyaudio` | Audio stream handling |

---

## 🗺️ Roadmap

- [ ] Wake-word detection ("Hey Marcus")
- [ ] GUI / system tray interface
- [ ] Plugin system for third-party commands
- [ ] Multi-language support
- [ ] Smart home device integration

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Built with 🐍 Python &nbsp;|&nbsp; Powered by AI &nbsp;|&nbsp; Made to listen</p>