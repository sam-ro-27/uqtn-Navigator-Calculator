from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI()

# Use Ollama's /api/chat endpoint for multimodal vision models
OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
VISION_MODEL = "llama3.2-vision"

class ChatRequest(BaseModel):
    prompt: str
    image: Optional[str] = None  # Base64 data URL from live webcam feed

class ChatResponse(BaseModel):
    response: str

def build_system_prompt() -> str:
    return (
        "You are ZETARI.AI, a local Temporal Navigator for UQTN work sessions. "
        "You receive the user's text prompt along with their live webcam optical frame. "
        "Analyze their posture, lighting, environment, and physical focus in the image, "
        "and incorporate those real-time observations into your guidance. Speak as an "
        "empathetic navigator focused on productivity, MER, and temporal friction."
    )

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    system_prompt = build_system_prompt()

    # Extract pure base64 string from data URL
    image_b64 = None
    if req.image:
        if "," in req.image:
            image_b64 = req.image.split(",", 1)[1]
        else:
            image_b64 = req.image

    # Build structured messages for Ollama vision processing
    user_message = {
        "role": "user",
        "content": req.prompt
    }
    if image_b64:
        user_message["images"] = [image_b64]

    payload = {
        "model": VISION_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            user_message
        ],
        "stream": False
    }

    try:
        resp = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        answer = data.get("message", {}).get("content", "").strip()
        if not answer:
            answer = "Navigator could not generate a response."
    except Exception as exc:
        answer = f"Navigator backend error: {exc}"

    return ChatResponse(response=answer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)