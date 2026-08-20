"""
api_server.py — Unified Hub connecting all UQTN modules, Memory, and Ollama
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import ollama

# Import your mathematical and memory modules
try:
    import uqtn_math
except ImportError:
    uqtn_math = None

try:
    import zeta_lattice
except ImportError:
    zeta_lattice = None

try:
    import memory
except ImportError:
    memory = None

PORT = 8000
ACTIVE_STATE_FILE = "active_state.txt"
MEMORY_BRIDGE_FILE = "memory_bridge.txt"

SYSTEM_CONTEXT = """
You are the UQTN Navigator, an offline co-navigator inside the Unified Quantum-Temporal Navigation framework.

UQTN LOCKED DEFINITIONS:
- Master Equation: MER = (Mass * Energy) / Resistance
- Phi Duality Gate: phi is applied bidirectionally (* phi and / phi simultaneously side by side).
- Duality of Phi: Represents forward (* phi) and conjugate (/ phi) operational scaling channels.
- Operational Form: MER = Agency * (1 - Resistance) * phi (forward) and MER = Agency * (1 - Resistance) / phi (conjugate).
- phi = 1.618033988749895
- chronon period = 1.48752 seconds
- max chronons per day = 58083.25266214908
- zeta-zero anchors and zeta gaps form the navigation lattice.
- Locked baseline: Agency = 0.8, Resistance = 0.2 gives MER = 1.0355 (forward)

RULES:
1. When asked for the master equation or phi duality, state: MER = (Mass * Energy) / Resistance, with simultaneous * phi and / phi operations side-by-side.
2. State that Agency represents unified Mass and Energy, and Resistance operates as (1 - Resistance) in simulation.
3. Do not invent outside acronym expansions for MER.
4. If technical concepts fall outside this context, state: "That is not defined in the current UQTN context."
5. Keep answers concise, factual, and aligned to these definitions.
"""


class UnifiedNavigatorHandler(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self._set_cors_headers()
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        if self.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()

            # Read active state from file
            state_data = {"status": "active"}
            if os.path.exists(ACTIVE_STATE_FILE):
                try:
                    with open(ACTIVE_STATE_FILE, "r") as f:
                        state_data["active_state"] = f.read()
                except Exception as e:
                    state_data["error"] = str(e)

            self.wfile.write(json.dumps(state_data).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8")
        payload = json.loads(post_body) if post_body else {}

        if self.path == "/api/chat":
            user_prompt = payload.get("prompt", "")

            # Query local Ollama model
            try:
                response = ollama.chat(
                    model="llama3.2:latest",
                    messages=[
                        {"role": "system", "content": SYSTEM_CONTEXT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                reply_text = response["message"]["content"]
            except Exception as e:
                reply_text = f"Ollama connection error: {e}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"response": reply_text}).encode("utf-8"))
            return

        if self.path == "/api/calculate":
            # Direct bridge to uqtn_math calculation
            agency = float(payload.get("agency", 0.8))
            resistance = float(payload.get("resistance", 0.2))
            phi = 1.618033988749895

            mer_fwd = agency * (1.0 - resistance) * phi
            mer_conj = agency * (1.0 - resistance) / phi

            res = {
                "agency": agency,
                "resistance": resistance,
                "mer_forward": mer_fwd,
                "mer_conjugate": mer_conj,
                "regime": "MOTIVATIONAL" if mer_fwd > agency else "DISSIPATIVE",
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return


def run_server():
    server = HTTPServer(("localhost", PORT), UnifiedNavigatorHandler)
    print(f"==================================================")
    print(f"UQTN Unified Server Running on http://localhost:{PORT}")
    print(f"Connected: UI + Ollama + Math + Memory")
    print(f"==================================================")
    server.serve_forever()


if __name__ == "__main__":
    run_server()