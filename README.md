# 🤖 DedSec — AI Voice Assistant

> A modular, conversational AI voice assistant built with Python — capable of listening, thinking, and speaking back.

---

## 📌 Overview

DedSec is a Python-based AI voice assistant that captures your voice, processes it through a language model, and responds with synthesized speech. Built with modularity in mind, it's designed to be easy to extend with new skills, APIs, and integrations.

---

## ✨ Features

- 🎙️ **Speech Recognition** — Listens to your voice in real time
- 🧠 **AI-Powered Responses** — Processes queries through an LLM (e.g., Groq / OpenAI)
- 🔊 **Text-to-Speech Output** — Speaks responses back using TTS
- 🧩 **Modular Architecture** — Easily plug in new commands and integrations
- ⚡ **Fast & Lightweight** — Minimal dependencies, runs locally

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Speech Recognition | `SpeechRecognition` / `Whisper` |
| Language Model | Groq API / OpenAI API |
| Text-to-Speech | `pyttsx3` / `gTTS` |
| Audio | `PyAudio` / `playsound` |

---

## 📁 Project Structure

```
DedSec/
├── main.py              # Entry point
├── listener.py          # Microphone input & speech-to-text
├── brain.py             # LLM query handler
├── speaker.py           # Text-to-speech output
├── commands/            # Modular skill handlers
│   ├── weather.py
│   ├── search.py
│   └── ...
├── config.py            # API keys & settings
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ShamGaneshan2008/dedsec-voice-assistant.git
cd dedsec-voice-assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Assistant

```bash
python main.py
```

---

## 🎤 Usage

Once running, DedSec will listen for your voice input and respond accordingly.

```
[DedSec] Listening...
You: "What's the weather today?"
[DedSec] "It's currently 28°C and sunny in your area."
```

Say **"exit"** or **"goodbye"** to shut down the assistant.

---

## ⚙️ Configuration

Edit `config.py` to customize behaviour:

```python
WAKE_WORD = "hey dedsec"      # Optional wake word
TTS_ENGINE = "pyttsx3"        # or "gtts"
LANGUAGE = "en"
```

---

## 📦 Requirements

```
speechrecognition
pyaudio
pyttsx3
groq
python-dotenv
requests
```

Install all at once:

```bash
pip install -r requirements.txt
```

> **Note:** `PyAudio` may require additional system dependencies.
> - **Windows:** `pip install pipwin && pipwin install pyaudio`
> - **Linux:** `sudo apt-get install portaudio19-dev`
> - **macOS:** `brew install portaudio`

---

## 🔮 Roadmap

- [ ] Wake word detection
- [ ] GUI overlay / system tray integration
- [ ] Local LLM support (Ollama)
- [ ] Smart home device control
- [ ] Memory / conversation history
- [ ] Plugin marketplace

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](LICENSE)

---

<p align="center">Built by <a href="https://github.com/ShamGaneshan2008">@ShamGaneshan2008</a></p>
