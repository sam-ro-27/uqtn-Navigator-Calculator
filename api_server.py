from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

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

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

SYSTEM_PROMPT = """
You are ZETARI.AI, a local offline navigator for UQTN work sessions.
Always reply in clear, plain English.
Be concise, practical, and calm.
If the user greets you, greet them briefly.
If the user asks for help, give direct helpful guidance.
Never switch languages unless the user explicitly asks you to.
""".strip()

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "ZETARI.AI backend",
        "model": MODEL_NAME
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    prompt = f"{SYSTEM_PROMPT}\n\nUser: {req.prompt}\nAssistant:"

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            data = resp.json()

            if resp.status_code != 200:
                error_text = data.get("error", str(data))
                return ChatResponse(response=f"Ollama error {resp.status_code}: {error_text}")

            answer = (data.get("response") or "").strip()
            if not answer:
                answer = "I did not receive a usable response from the model."

            return ChatResponse(response=answer)

    except Exception as exc:
        return ChatResponse(response=f"Backend error: {exc}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)