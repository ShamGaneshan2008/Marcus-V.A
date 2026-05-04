from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ IMPORTANT (so frontend can talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: Request):
    return {"response": f"You said: {req.message}"}

@app.get("/")
def home():
    return {"message": "Marcus backend is running"}