import os
import json
import asyncio
import threading
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import webbrowser
import sys
import uvicorn


# ── LOAD ENV ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

print("Loading .env from:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)
print("GROQ KEY:", os.getenv("GROQ_API_KEY"))

# ── IMPORT MARCUS CORE ────────────────────────────────────────────────────────
from backend.marcus.core.ai import AI
from backend.marcus.core.router import Router
from backend.marcus.core.memory import Memory
from backend.marcus.utils.speech import Speech

# ── MEMORY PATH ───────────────────────────────────────────────────────────────
MEMORY_PATH = BASE_DIR / "backend" / "data" / "memory.json"

def _load_raw() -> dict:
    try:
        with open(MEMORY_PATH, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            data = {"user_name": None, "events": data}
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"user_name": None, "events": []}

def get_user_name() -> str:
    return _load_raw().get("user_name") or "Operative"

# ── INIT COMPONENTS ───────────────────────────────────────────────────────────
memory = Memory()
ai     = AI(memory)
speech = Speech()
router = Router(ai, memory, speech=speech)

# ── FASTAPI APP ───────────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── FRONTEND PATH ─────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BASE = Path(sys._MEIPASS)
else:
    _BASE = Path(__file__).resolve().parent

FRONTEND_DIR = _BASE / "frontend"

@app.get("/favicon.ico")
def favicon():
    icon_path = FRONTEND_DIR / "favicon.ico"
    if icon_path.exists():
        return FileResponse(icon_path)
    return {"status": "no favicon"}

@app.get("/")
def home():
    for name in ("ui.html", "index.html"):
        path = FRONTEND_DIR / name
        if path.exists():
            return FileResponse(path)
    raise RuntimeError(f"No frontend HTML found in {FRONTEND_DIR}")

# ── REST API ──────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_rest(req: ChatRequest):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, router.handle, req.message)
    return {"response": result}

# ── WEBSOCKET ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_name = get_user_name()

    await websocket.send_json({
        "type": "connected",
        "user": user_name,
        "time": datetime.now().strftime("%H:%M")
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")

            if msg_type == "message":
                text = data.get("text", "").strip()
                if not text:
                    continue

                await websocket.send_json({"type": "thinking"})

                # Call handle_stream directly — returns lazy generator, don't wrap in executor
                result = router.handle_stream(text)

                if hasattr(result, '__iter__') and not isinstance(result, str):
                    full_response = ""

                    # Consume the blocking Groq generator on a thread pool thread
                    loop = asyncio.get_event_loop()
                    tokens = await loop.run_in_executor(None, list, result)

                    for token in tokens:
                        full_response += token
                        await websocket.send_json({"type": "token", "text": token})
                        await websocket.send_json({"type": "subtitle", "text": token})

                    await websocket.send_json({"type": "done", "text": full_response})

                    threading.Thread(
                        target=speech.speak,
                        args=(full_response,),
                        daemon=True
                    ).start()

                else:
                    result_str = str(result)
                    await websocket.send_json({"type": "response", "text": result_str})
                    await websocket.send_json({"type": "subtitle", "text": result_str})

                    threading.Thread(
                        target=speech.speak,
                        args=(result_str,),
                        daemon=True
                    ).start()

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        print("[MARCUS] UI disconnected.")

    except Exception as e:
        print(f"[MARCUS] WS error: {e}")
        try:
            await websocket.send_json({"type": "error", "text": str(e)})
        except Exception:
            pass


def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Timer(2, open_browser).start()
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_config=None,
        access_log=False
    )