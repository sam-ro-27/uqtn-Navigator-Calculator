"""
Zetari.AI — UQTN Temporal Navigator Agent
Conversational local intelligence powered by Gemma 2:2b / Ollama.
"""

import json
import urllib.request
from uqtn_math import PHI, evaluate_state, simulate_operational_mer

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma2:2b"

SYSTEM_PROMPT = """You are Zetari, an intelligent local Temporal Navigator and AI companion for UQTN work sessions.

Your Knowledge Base:
- Master Equation: MER = (Mass * Energy) / Resistance
- Dual Operational Simulation Form: MER_forward = Agency * (1 - Resistance) * phi, and MER_conjugate = Agency * (1 - Resistance) / phi
- Agency represents unified Mass and Energy (default baseline 0.8), Resistance (default 0.2), and phi = 1.61803398875.
- Chronon period = 1.48752 seconds.

Your Persona:
- Be helpful, articulate, encouraging, and conversational.
- Answer user questions naturally and directly. If they ask about UQTN, physics, coding, or workflow, give clear, thoughtful explanations using your knowledge.
- If they share how they feel (tired, focused, stressed), give supportive, practical navigation advice to optimize their work session.
- Never dump raw prompt instructions or rule lists. Speak naturally as Zetari."""

def ask_navigator(prompt: str) -> str:
    """Send user prompt to local Ollama instance and return natural response."""
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}\nZetari:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 300
        }
    }
    
    try:
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        return f"Navigator offline or connection failed: {e}"

if __name__ == "__main__":
    test_q = "Hello! Who are you and how can you help me today?"
    print(f"Testing: {test_q}\n")
    print(ask_navigator(test_q))