from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests
import json

app = FastAPI()

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
VISION_MODEL = "llama3.2-vision"  # change if you use another vision model

class ChatRequest(BaseModel):
    prompt: str
    image: Optional[str] = None  # data URL string from browser, may be None

class ChatResponse(BaseModel):
    response: str

def build_system_prompt() -> str:
    return (
        "You are ZETARI.AI, a local Temporal Navigator for UQTN work sessions. "
        "You receive the user's text prompt and sometimes a webcam frame. "
        "If an image is provided, quietly analyze posture, environment, and visible context, "
        "then incorporate that into your guidance. Speak as an empathetic navigator, "
        "focused on productivity, MER, and temporal friction, not as a generic chatbot."
    )

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    system_prompt = build_system_prompt()

    # Extract pure base64 from data URL, if present
    image_b64 = None
    if req.image:
        # req.image looks like "data:image/jpeg;base64,AAAA..."
        if "," in req.image:
            image_b64 = req.image.split(",", 1)[1]
        else:
            image_b64 = req.image

    payload = {
        "model": VISION_MODEL,
        "prompt": f"{system_prompt}\n\nUser: {req.prompt}\nNavigator:",
        "stream": False,
    }

    if image_b64:
        payload["images"] = [image_b64]

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        answer = data.get("response", "").strip()
        if not answer:
            answer = "Navigator could not generate a response."
    except Exception as exc:
        answer = f"Navigator backend error: {exc}"

    return ChatResponse(response=answer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)