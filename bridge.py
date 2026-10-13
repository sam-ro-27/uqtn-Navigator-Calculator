"""
bridge.py — connection between Dirac Internet Central and the
Krimoxous backend.

The bridge lets the hub draw on the living system: it can pull the
latest vision observation into the RIGHT hemisphere's flow and send
chat through the backend's Ollama models for the LEFT hemisphere.

Everything here is optional and defensive: if the backend is down,
the bridge reports it instead of raising. httpx is imported lazily
so the package imports cleanly without it.
"""

from pathlib import Path


def _httpx():
    try:
        import httpx
        return httpx
    except ImportError:
        return None


class KrimoxousBridge:
    """
    Thin client over the Krimoxous backend (default 127.0.0.1:8000).

    Methods return dicts shaped for the hub's chiral split:
      vision_observation() -> {"image": <latest description>}
      chat(text)           -> {"text": <model reply>}
    """

    def __init__(self, backend_url="http://127.0.0.1:8000", timeout=90.0):
        self.backend_url = backend_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Backend probes
    # ------------------------------------------------------------------

    def alive(self):
        """True if the Krimoxous backend answers."""
        httpx = _httpx()
        if httpx is None:
            return False
        try:
            r = httpx.get(f"{self.backend_url}/", timeout=5.0)
            return r.status_code == 200
        except Exception:
            return False

    def warmup(self):
        """Hit the backend warmup endpoint if it exists (v2 patch+)."""
        httpx = _httpx()
        if httpx is None:
            return {"warmed": False, "error": "httpx not installed"}
        try:
            r = httpx.get(f"{self.backend_url}/api/warmup", timeout=120.0)
            if r.status_code != 200:
                return {"warmed": False, "status": r.status_code}
            try:
                data = r.json()
            except ValueError:
                return {"warmed": True, "status": r.status_code}
            return data if isinstance(data, dict) else {"warmed": True, "status": r.status_code}
        except Exception as exc:
            return {"warmed": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Chiral feeds
    # ------------------------------------------------------------------

    def vision_observation(self):
        """
        RIGHT-hemisphere feed: the latest optical observation text.
        Tries the backend /api/vision endpoint first, then falls back to
        a local latest_vision.txt file when running offline.
        """
        httpx = _httpx()
        if httpx is not None:
            try:
                r = httpx.get(f"{self.backend_url}/api/vision", timeout=self.timeout)
                if r.status_code == 200:
                    try:
                        data = r.json()
                    except ValueError:
                        data = {}
                    if isinstance(data, dict):
                        value = (
                            data.get("image")
                            or data.get("text")
                            or data.get("observation")
                            or data.get("description")
                            or ""
                        )
                        if value:
                            return {"image": value, "note": data.get("note", "backend vision feed")}
            except Exception:
                pass

        local_path = Path(__file__).with_name("latest_vision.txt")
        try:
            if local_path.exists():
                value = local_path.read_text(encoding="utf-8").strip()
                if value:
                    return {"image": value, "note": "local latest_vision.txt"}
        except Exception:
            pass

        return {"image": "", "note": "wire to backend vision feed"}

    def chat(self, text):
        """
        LEFT-hemisphere feed: send text through the backend chat.
        Returns {"text": reply} or {"text": "", "error": ...}.
        """
        if not isinstance(text, str):
            text = str(text)

        httpx = _httpx()
        if httpx is None:
            return {"text": "", "error": "httpx not installed"}
        try:
            r = httpx.post(
                f"{self.backend_url}/api/chat",
                json={"prompt": text},
                timeout=self.timeout,
            )
            if r.status_code != 200:
                return {"text": "", "error": f"backend returned {r.status_code}"}
            try:
                data = r.json()
            except ValueError:
                return {"text": "", "error": "backend did not return JSON"}
            if isinstance(data, dict):
                response = (
                    data.get("response")
                    or data.get("reply")
                    or data.get("text")
                    or data.get("message")
                    or ""
                )
                if response:
                    return {"text": response}
                if "error" in data:
                    return {"text": "", "error": data["error"]}
            return {"text": "", "error": "empty response from backend"}
        except Exception as exc:
            return {"text": "", "error": str(exc)}

    def hub_payload(self, text="", image=""):
        """One chiral-split payload, ready for hub.cycle()."""
        return {"text": text, "image": image}


def main():
    # Example usage of KrimoxousBridge class
    bridge = KrimoxousBridge()

    # Check if the backend is alive
    print("Backend Alive:", bridge.alive())

    # Warm up the backend
    warmup_result = bridge.warmup()
    print("Warmup Result:", warmup_result)

    # Get the latest vision observation
    vision_result = bridge.vision_observation()
    print("Vision Observation:", vision_result)

    # Send a chat message and get the reply
    chat_result = bridge.chat("Hello, how are you?")
    print("Chat Result:", chat_result)


if __name__ == "__main__":
    main()