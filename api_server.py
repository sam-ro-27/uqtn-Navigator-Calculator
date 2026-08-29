from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from pathlib import Path
import json

app = FastAPI(title="ZETARI.AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = os.getenv("ZETARI_MODEL", "llama3.2:latest")
BASE_DIR = Path(__file__).resolve().parent

PROMPT_FILES = [
    "core_memory.txt",
    "memory_bridge.txt",
    "uqtn_math.txt",
    "session_delta.txt",
]

STATE_FILES = [
    "project.json",
    "navigator_history.json",
]

CODE_MODULES = [
    "offline_navigator.py",
    "uqtn_core.py",
    "uqtn_math.py",
    "zeta_lattice.py",
    "uqtn_simultaneous_engine.py",
    "uqtn_calculator.py",
    "memory.py",
    "rotor_sim.py",
    "main.py",
]

SYSTEM_PROMPT = """
You are ZETARI.AI, a local offline navigator for UQTN work sessions and state guidance.
Use the provided UQTN context as authoritative project meaning.
Prefer plain English unless the user asks for technical detail.
If a term exists in loaded context, use that meaning.
If a runtime calculation is available, use it instead of guessing.
If visual analysis is unavailable for a request, say so clearly.
"""

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

def read_text_file(name):
    path = BASE_DIR / name
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore").strip()
    except:
        return ""

def read_json_file(name):
    path = BASE_DIR / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except:
        return {}

def load_prompt_context():
    parts = [SYSTEM_PROMPT.strip()]
    for name in PROMPT_FILES:
        text = read_text_file(name)
        if text:
            parts.append(f"[{name}]\n{text}")
    return "\n\n".join(parts)

def load_state_context():
    state = {}
    for name in STATE_FILES:
        state[name] = read_json_file(name)
    return state

def build_runtime_summary():
    available = []
    for name in CODE_MODULES:
        if (BASE_DIR / name).exists():
            available.append(name)
    return "Available local runtime modules: " + ", ".join(available)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "ZETARI.AI backend",
        "model": MODEL_NAME
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    prompt_context = load_prompt_context()
    state_context = load_state_context()
    runtime_summary = build_runtime_summary()

    prompt = f"""
{prompt_context}

{runtime_summary}

Current local state:
{json.dumps(state_context, ensure_ascii=False)[:4000]}

User: {req.prompt}
Assistant:
""".strip()

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            data = resp.json()

        if resp.status_code != 200:
            return ChatResponse(response=f"Ollama error {resp.status_code}: {data}")

        answer = (data.get("response") or "").strip()
        if not answer:
            answer = "I did not receive a usable response from the model."

        return ChatResponse(response=answer)

    except Exception as exc:
        return ChatResponse(response=f"Backend error: {exc}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)