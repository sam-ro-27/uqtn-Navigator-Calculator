from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use Ollama's /api/generate endpoint for vision
OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"

# IMPORTANT: set to EXACTLY what `ollama list` shows
VISION_MODEL = os.getenv("ZETARI_MODEL", "llama3.2-vision")

class ChatRequest(BaseModel):
    prompt: str
    image: Optional[str] = None  # data URL from webcam

class ChatResponse(BaseModel):
    response: str

def build_system_prompt() -> str:
    return (
        "You are ZETARI.AI, a local Temporal Navigator for UQTN work sessions. "
        "IMPORTANT: Always respond in clear, plain English only. "
        "Never answer in another language unless the user explicitly asks you to translate. "
        "You receive the user's text prompt and sometimes a live webcam frame. "
        "When an image is present, analyze only visible facts in the frame, such as "
        "objects, lighting, posture, facial expression, and the environment. "
        "Do not claim you see a camera frame if no image was received. "
        "Give concise, helpful guidance based on the user's actual question."
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    system_prompt = build_system_prompt()

    # Extract pure base64 string from data URL, if any
    image_b64 = None
    if req.image:
        if "," in req.image:
            image_b64 = req.image.split(",", 1)[1]
        else:
            image_b64 = req.image

    full_prompt = f"{system_prompt}\n\nUSER: {req.prompt}\n\nASSISTANT:"

    payload = {
        "model": VISION_MODEL,
        "prompt": full_prompt,
        "stream": False,
    }

    # Attach image at root, per Ollama vision docs
    if image_b64:
        payload["images"] = [image_b64]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(OLLAMA_GENERATE_URL, json=payload, timeout=90.0)
            data = resp.json()

            if resp.status_code != 200:
                # Show Ollama's own error message if present
                err_msg = data.get("error") or str(data)
                answer = f"Ollama error {resp.status_code}: {err_msg}"
            else:
                answer = data.get("response", "").strip()
                if not answer:
                    answer = "Navigator could not generate a response."
    except Exception as exc:
        answer = f"Navigator backend error: {exc}"

    return ChatResponse(response=answer)

@app.get("/")
def root():
    return {"status": "ZETARI.AI backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)