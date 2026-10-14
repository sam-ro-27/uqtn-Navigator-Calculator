# pyright: reportMissingImports=false
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import ollama
from pathlib import Path
import json
import sys
BASE_DIR = Path(__file__).resolve().parent

# ----------------------------------------------------------------------
# Dirac Internet Central — merged hub (user: "just merge them")
# Tries, in order: (1) dirac_internet_central/ package beside this file,
# (2) the 15 modules as flat .py files beside this file (his layout),
# (3) graceful degradation when neither is present.
# NOTE: in the flat layout, hemisphere_py.bin must be renamed to
# hemisphere.py for the relative imports to resolve.
# ----------------------------------------------------------------------
def _load_dirac():
    # (1) Proper package layout.
    try:
        from dirac_internet_central import (
            DiracInternetCentral,
            fluid_state_snapshot,
        )
        try:
            from dirac_internet_central import dirac_router as _router
        except Exception:
            _router = None
        return DiracInternetCentral, fluid_state_snapshot, _router, "package"
    except ImportError:
        pass

    # (2) Flat layout: synthesize the package from loose modules so the
    # relative imports inside them (from .config import ...) resolve.
    try:
        import types
        pkg = types.ModuleType("dirac_internet_central")
        pkg.__path__ = [str(BASE_DIR)]
        sys.modules["dirac_internet_central"] = pkg
        from dirac_internet_central.central import DiracInternetCentral
        from dirac_internet_central.state import fluid_state_snapshot
        try:
            from dirac_internet_central.api import router as _router
        except Exception:
            _router = None
        # Verify the key modules actually resolved (hemisphere.py!).
        from dirac_internet_central import hemisphere as _hem_check  # noqa
        return DiracInternetCentral, fluid_state_snapshot, _router, "flat"
    except Exception:
        sys.modules.pop("dirac_internet_central", None)
        return None, None, None, "missing"


DiracInternetCentral, fluid_state_snapshot, _dirac_router, _dirac_layout = _load_dirac()
_HAVE_DIRAC = DiracInternetCentral is not None


app = FastAPI(title="Krimoxous.AI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dirac hub: one shared instance for the merged server.
dirac_hub = DiracInternetCentral() if _HAVE_DIRAC else None
if _dirac_router is not None and dirac_hub is not None:
    try:
        _dirac_router.hub = dirac_hub
        app.include_router(_dirac_router)
    except Exception:
        pass


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = os.getenv("KRIMOXOUS_MODEL", "llama3.2:latest")
VISION_MODEL_NAME = os.getenv("KRIMOXOUS_VISION_MODEL", "llava")

latest_vision_description = {"text": None}
VISION_TEXT_FILE = BASE_DIR / "latest_vision.txt"


def save_vision_text(text):
    latest_vision_description["text"] = text
    try:
        VISION_TEXT_FILE.write_text(text or "", encoding="utf-8")
    except Exception:
        pass


def get_vision_text():
    text = latest_vision_description.get("text")
    if text:
        return text
    try:
        if VISION_TEXT_FILE.exists():
            return VISION_TEXT_FILE.read_text(encoding="utf-8").strip() or None
    except Exception:
        pass
    return None

# NOTE: memory_bridge.txt already aggregates core_memory.txt,
# active_state.txt and session_delta.txt -- listing them separately
# duplicated ~half the prompt on every request. Keep it to the bridge.
PROMPT_FILES = [
    "memory_bridge.txt",
    "uqtn_math.txt",
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
You are Krimoxous.AI, a local offline navigator for UQTN work sessions and state guidance.
Use the provided UQTN context as authoritative project meaning.
Prefer plain English unless the user asks for technical detail.
If a term exists in loaded context, use that meaning.
If a runtime calculation is available, use it instead of guessing.
If visual analysis is unavailable for a request, say so clearly.
The "Available local runtime modules" list below only means these files exist on disk.
It does NOT mean they are imported, running, tested, or integrated in any way.
Never claim a module is "integrated," "active," or "tested" unless the user's
message itself states that as fact. Never claim to enable, monitor, or watch
the file system, since you have no such capability.
"""


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    response: str


class DiracChatRequest(BaseModel):
    prompt: str
    image: str = ""


class DiracChatResponse(BaseModel):
    response: str
    fused: dict = {}
    continuity_holds: bool = True


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
    return "Files present on disk (not necessarily imported or running): " + ", ".join(available)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Krimoxous.AI backend",
        "model": MODEL_NAME,
        "vision_patch": "v2",
        "dirac": (_dirac_layout if dirac_hub is not None else "missing"),
    }


@app.get("/api/warmup")
async def warmup():
    """Force-load the Ollama model now so the first real chat is fast.
    Called once by the frontend on page load (fire-and-forget)."""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": "ok",
                "stream": False,
                "keep_alive": "30m",
            })
            warmed = resp.status_code == 200
    except Exception:
        warmed = False
    return {"warmed": warmed, "model": MODEL_NAME}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    prompt_context = load_prompt_context()
    state_context = load_state_context()
    runtime_summary = build_runtime_summary()
    vision_text = get_vision_text() or "No recent observation"


    prompt = f"""
{prompt_context}


{runtime_summary}


Current optical observation (if available): {vision_text}


Current local state:
{json.dumps(state_context, ensure_ascii=False)[:4000]}


User: {req.prompt}
Assistant:
""".strip()


    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "30m",
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


@app.post("/api/dirac/chat", response_model=DiracChatResponse)
def dirac_chat(req: DiracChatRequest):
    """Chat through the Dirac hub: prompt -> chiral split -> hemispheres
    -> corpus callosum fusion -> composed reply. Merged from dirac_server."""
    if dirac_hub is None:
        return DiracChatResponse(
            response="Dirac hub not loaded: dirac_internet_central/ folder missing.",
            continuity_holds=False,
        )
    try:
        result = dirac_hub.cycle({"text": req.prompt, "image": req.image})
        fused = result["fused"]
        return DiracChatResponse(
            response=_compose_dirac_reply(fused),
            fused=fused,
            continuity_holds=result["continuity_holds"],
        )
    except Exception as exc:
        return DiracChatResponse(
            response=f"Dirac hub error: {exc}",
            continuity_holds=False,
        )


@app.post("/api/dirac/ingest")
def dirac_ingest(payload: dict):
    """Raw internet information -> one hub cycle."""
    if dirac_hub is None:
        return {"error": "Dirac hub not loaded"}
    try:
        return dirac_hub.cycle(payload)
    except Exception as exc:
        return {"error": str(exc)}


@app.get("/api/dirac/state")
def dirac_state():
    """Fluid snapshot: density, current, continuity, throughput."""
    if dirac_hub is None or fluid_state_snapshot is None:
        return {"error": "Dirac hub not loaded"}
    return fluid_state_snapshot(dirac_hub)


def _compose_dirac_reply(fused):
    """INTERPRETIVE: fuse the two hemisphere readings into prose."""
    analytic = (fused.get("analytic") or {})
    holistic = (fused.get("holistic") or {})
    parts = []
    analysis = analytic.get("analysis", {})
    if analysis:
        parts.append(
            "Left reading (analytic): "
            f"{analysis.get('words', 0)} words, "
            f"{len(analytic.get('terms', []))} salient terms."
        )
    impression = holistic.get("impression", {})
    if impression:
        parts.append(
            "Right reading (holistic): "
            f"{impression.get('count', 0)} elements present."
        )
    parts.append(fused.get("fused_note", ""))
    return " ".join(p for p in parts if p)

@app.post("/api/vision")
async def vision_endpoint(image: UploadFile):
    image_bytes = await image.read()
    try:
        response = ollama.chat(
            model=VISION_MODEL_NAME,
            messages=[{
                "role": "user",
                "content": (
                    "Describe this webcam scene in one short sentence. "
                    "Note posture, apparent focus or fatigue, lighting, and room "
                    "environment if visible. Do not invent details you cannot see."
                ),
                "images": [image_bytes]
            }]
        )
        description = response["message"]["content"]
        save_vision_text(description)
    except Exception as exc:
        return {"description": None, "error": str(exc)}

    return {"description": description}


if __name__ == "__main__":
    import uvicorn
    HOST = os.getenv("KRIMOXOUS_HOST", "0.0.0.0")
    PORT = int(os.getenv("KRIMOXOUS_PORT", "8000"))
    # 0.0.0.0 = internet-reachable (his requirement, token-free).
    # Set KRIMOXOUS_HOST=127.0.0.1 to go back to local-only.
    uvicorn.run(app, host=HOST, port=PORT)