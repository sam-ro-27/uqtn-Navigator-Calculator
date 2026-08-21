from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx

app = FastAPI()

# CORS frequency injection to eliminate boundary friction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Opens the bridge to all local ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # Utilizing async httpx to maintain optimal thermodynamic flow
        async with httpx.AsyncClient() as client:
            resp = await client.post(OLLAMA_CHAT_URL, json=payload, timeout=90.0)
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("message", {}).get("content", "").strip()
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