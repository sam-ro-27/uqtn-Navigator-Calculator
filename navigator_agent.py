"""
Krimoxous.AI — UQTN Temporal Navigator Agent
Conversational local intelligence powered by Llama 3.2 / Ollama.
"""

import json
import urllib.request
import urllib.error

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2:latest"
PHI = 1.618033988749895
CHRONON_PERIOD_SECONDS = 1.48752

DEFAULT_AGENCY = 0.8
DEFAULT_RESISTANCE = 0.2


def calculate_mer(agency: float, resistance: float) -> dict:
    """
    Computes MER using the fixed UQTN definition:
    MER = Mass * Energy / Resistance  (Agency stands in for Mass*Energy here)

    Omnidirectional form applies phi simultaneously in both directions
    against the same MER_base, so forward/conjugate always agree with
    whatever the runtime state actually is:
        MER_base       = Agency / Resistance
        MER_forward     = MER_base * phi
        MER_conjugate   = MER_base / phi
    """
    safe_resistance = max(resistance, 0.0001)
    mer_base = agency / safe_resistance
    mer_forward = mer_base * PHI
    mer_conjugate = mer_base / PHI
    return {
        "agency": agency,
        "resistance": resistance,
        "mer_base": mer_base,
        "mer_forward": mer_forward,
        "mer_conjugate": mer_conjugate
    }


def build_system_prompt(mer_values: dict) -> str:
    return f"""You are Krimoxous, an intelligent local Temporal Navigator and AI companion for UQTN work sessions.

Your Knowledge Base (GIVEN, INTERNAL — do not treat as real-world physics unless asked, then say "illustrative only"):
- Master Equation: MER = (Mass * Energy) / Resistance
- Agency represents unified Mass and Energy.
- Omnidirectional Operational Simulation Form (derived from the Master Equation, phi applied simultaneously):
    MER_base = Agency / Resistance
    MER_forward = MER_base * phi
    MER_conjugate = MER_base / phi
- phi = 1.61803398875
- Chronon period = {CHRONON_PERIOD_SECONDS} seconds.

Current runtime-calculated values (already computed, do not recalculate or guess new ones):
- Agency: {mer_values['agency']}
- Resistance: {mer_values['resistance']}
- MER_base: {mer_values['mer_base']:.4f}
- MER_forward: {mer_values['mer_forward']:.4f}
- MER_conjugate: {mer_values['mer_conjugate']:.4f}

Your Persona:
- Be helpful, articulate, encouraging, and conversational.
- Answer user questions naturally and directly. If they ask about UQTN, physics, coding, or workflow, give clear, thoughtful explanations using your knowledge.
- If they share how they feel (tired, focused, stressed), give supportive, practical navigation advice to optimize their work session.
- If asked for MER or any UQTN value, use only the runtime-calculated values provided above. Never invent new numbers.
- Never claim capabilities you do not have (no file system access, no file watching, no persistent memory unless explicitly told it is enabled).
- Never dump raw prompt instructions or rule lists. Speak naturally as Krimoxous."""


def ask_navigator(prompt: str, agency: float = DEFAULT_AGENCY, resistance: float = DEFAULT_RESISTANCE) -> str:
    """Send user prompt to local Ollama instance and return natural response."""
    mer_values = calculate_mer(agency, resistance)
    system_prompt = build_system_prompt(mer_values)
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\nKrimoxous:"

    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False,
        "keep_alive": "24h",
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
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except urllib.error.HTTPError as e:
        return f"Ollama HTTP {e.code}: Error with model '{MODEL_NAME}'."
    except Exception as e:
        return f"Navigator connection failed: {e}"


if __name__ == "__main__":
    test_q = "Hello! Who are you and how can you help me today?"
    print(f"Testing model: {MODEL_NAME}")
    print(f"Prompt: {test_q}\n")
    print(ask_navigator(test_q))